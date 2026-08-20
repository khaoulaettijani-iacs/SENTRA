import time
import os
import requests
from elasticsearch import Elasticsearch

# 1. Définition des variables d'environnement (Celles qui avaient disparu !)
ES_HOST = os.environ.get("ES_HOST", "http://elasticsearch:9200")
ML_API = os.environ.get("ML_API", "http://backend-api:8000")
RISK_API = os.environ.get("RISK_API", "http://risk-scoring-engine:8000")

print(f"[*] Démarrage du Correlation Engine SENTRA...")
print(f"[*] ES_HOST: {ES_HOST} | ML_API: {ML_API} | RISK_API: {RISK_API}")

ES = Elasticsearch(ES_HOST)

def find_flow(flow_id):
    """Recherche les métriques de trafic (flow) correspondant à une alerte."""
    if not flow_id:
        return None
    
    r = ES.search(index="suricata-*", query={
        "bool": {
            "must": [
                {"term": {"flow_id": flow_id}},
                {"term": {"event_type": "flow"}}
            ]
        }
    }, size=1)
    
    hits = r.get("hits", {}).get("hits", [])
    return hits[0]["_source"] if hits else None

def extract_features(flow):
    """Extrait les 8 features requises par les modèles ML (v2)."""
    age = max(flow["flow"].get("age", 1), 1)
    bts = flow["flow"].get("bytes_toserver", 0)
    btc = flow["flow"].get("bytes_toclient", 0)
    pts = flow["flow"].get("pkts_toserver", 0)
    ptc = flow["flow"].get("pkts_toclient", 0)
    
    return {
        "flow_duration": float(age), 
        "total_fwd_packets": float(pts), 
        "total_bwd_packets": float(ptc),
        "total_len_fwd": float(bts), 
        "total_len_bwd": float(btc),
        "flow_bytes_per_sec": float((bts + btc) / age), 
        "flow_packets_per_sec": float((pts + ptc) / age),
        "down_up_ratio": float(btc / bts) if bts > 0 else 0.0,
    }

# --- INITIALISATION DE LA LIGNE DE BASE TEMPORELLE ---
print("[*] Initialisation de la ligne de base temporelle...")
try:
    init_query = ES.search(
        index="suricata-*", 
        query={"term": {"event_type": "alert"}}, 
        sort=[{"@timestamp": "desc"}], 
        size=1 
    )
    if init_query["hits"]["hits"]:
        last_ts = init_query["hits"]["hits"][0]["_source"]["@timestamp"]
        print(f"[+] Ligne de base établie à l'alerte la plus récente : {last_ts}")
    else:
        last_ts = "now-24h"
        print("[!] Aucune alerte trouvée dans l'historique. Début de la recherche à : now-24h")
except Exception as e:
    print(f"[-] Erreur lors de l'initialisation : {e}")
    last_ts = "now-2m"

print("[+] Moteur en écoute (Polling: 10s)...")

while True:
    try:
        # Recherche des événements POSTÉRIEURS à last_ts
        query = {
            "bool": {
                "must": [
                    {"range": {"@timestamp": {"gt": last_ts}}},
                    {"term": {"event_type": "alert"}}
                ]
            }
        }
        
        results = ES.search(index="suricata-*", query=query, sort=[{"@timestamp": "asc"}], size=50)
        hits = results.get("hits", {}).get("hits", [])
        
        if hits:
            print(f"[*] {len(hits)} nouvelle(s) alerte(s) trouvée(s) depuis {last_ts}.")
        
        for hit in hits:
            alert = hit["_source"]
            flow_id = alert.get("flow_id")
            signature = alert.get("alert", {}).get("signature", "Inconnue")
            
            print(f"  -> Traitement Alerte: {signature} (Flow ID: {flow_id})")
            
            flow = find_flow(flow_id)
            if not flow:
                print(f"     [!] Flux réseau introuvable. En attente...")
                continue 

            # Appel aux APIs ML et Risk
            ml_payload = extract_features(flow)
            ml_result = requests.post(f"{ML_API}/score", json=ml_payload).json()

            risk_payload = {
                "ids_severity": alert.get("alert", {}).get("severity", 3),
                "mitre_tactic": alert.get("mitre", {}).get("tactic", "Unmapped"),
                "rf_proba": ml_result["rf_proba"],
                "iso_raw_score": ml_result["iso_raw_score"],
            }
            risk_result = requests.post(f"{RISK_API}/score-risk", json=risk_payload).json()

            correlated = {
                "@timestamp": alert["@timestamp"],
                "src_ip": alert.get("src_ip"), "dest_ip": alert.get("dest_ip"),
                "signature": signature,
                "mitre": alert.get("mitre", {}),
                "ml": ml_result, "risk": risk_result,
            }
            
            ES.index(index="correlated-events", document=correlated)
            print(f"     [SUCCESS] Indexé avec risque: {risk_result['risk_level']}")
            
            # Mise à jour de la date/heure
            last_ts = alert["@timestamp"]

    except Exception as e:
        print(f"[-] Erreur boucle : {e}")
        
    time.sleep(10)