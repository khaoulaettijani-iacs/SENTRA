import time
import os
import requests
from elasticsearch import Elasticsearch

ES_HOST = os.environ.get("ES_HOST", "http://elasticsearch:9200")
ML_API = os.environ.get("ML_API", "http://backend-api:8000")
RISK_API = os.environ.get("RISK_API", "http://risk-scoring-engine:8000")

print(f"[*] Démarrage du Correlation Engine SENTRA...")
print(f"[*] ES_HOST: {ES_HOST} | ML_API: {ML_API} | RISK_API: {RISK_API}")

ES = Elasticsearch(ES_HOST)

def find_flow(flow_id):
    """Recherche le log final du flux (s'il est déjà fermé)."""
    if not flow_id:
        return None
    r = ES.search(index="suricata-*", query={
        "bool": {"must": [{"term": {"flow_id": flow_id}}, {"term": {"event_type": "flow"}}]}
    }, size=1)
    hits = r.get("hits", {}).get("hits", [])
    return hits[0]["_source"] if hits else None

def extract_features(document):
    """Extrait les 8 features ML, qu'elles viennent d'un log 'flow' ou du snapshot d'une 'alert'"""
    flow = document.get("flow", {})
    # Si 'age' n'est pas encore calculé par Suricata, on assume 1 seconde
    age = max(float(flow.get("age", 1.0)), 1.0)
    bts = float(flow.get("bytes_toserver", 0))
    btc = float(flow.get("bytes_toclient", 0))
    pts = float(flow.get("pkts_toserver", 0))
    ptc = float(flow.get("pkts_toclient", 0))
    
    return {
        "flow_duration": age, 
        "total_fwd_packets": pts, 
        "total_bwd_packets": ptc,
        "total_len_fwd": bts, 
        "total_len_bwd": btc,
        "flow_bytes_per_sec": (bts + btc) / age, 
        "flow_packets_per_sec": (pts + ptc) / age,
        "down_up_ratio": (btc / bts) if bts > 0 else 0.0,
    }

# --- INITIALISATION ---
print("[*] Initialisation de la ligne de base temporelle...")
try:
    init_query = ES.search(index="suricata-*", query={"term": {"event_type": "alert"}}, sort=[{"@timestamp": "desc"}], size=1)
    if init_query["hits"]["hits"]:
        last_ts = init_query["hits"]["hits"][0]["_source"]["@timestamp"]
        print(f"[+] Ligne de base : {last_ts}")
    else:
        last_ts = "now-24h"
except Exception as e:
    last_ts = "now-2m"

print("[+] Moteur en écoute (Polling: 10s)...")

while True:
    try:
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
            print(f"[*] {len(hits)} nouvelle(s) alerte(s) trouvée(s).")
        
        for hit in hits:
            alert = hit["_source"]
            flow_id = alert.get("flow_id")
            signature = alert.get("alert", {}).get("signature", "Inconnue")
            
            print(f"  -> Traitement Alerte: {signature} (Flow ID: {flow_id})")
            
            # 1. On cherche le flux final
            target_data = find_flow(flow_id)
            
            # 2. Si le flux final n'est pas encore prêt, on utilise l'instantané de l'alerte !
            if not target_data:
                if "flow" in alert:
                    print("     [i] Utilisation du snapshot réseau en temps réel.")
                    target_data = alert
                else:
                    print("     [!] Aucun contexte réseau. Alerte ignorée.")
                    last_ts = alert["@timestamp"] # FIX CRITIQUE : on avance le temps quoi qu'il arrive
                    continue 

            # 3. Interroger les APIs
            ml_payload = extract_features(target_data)
            ml_result = requests.post(f"{ML_API}/score", json=ml_payload).json()

            risk_payload = {
                "ids_severity": alert.get("alert", {}).get("severity", 3),
                "mitre_tactic": alert.get("mitre", {}).get("tactic", "Unmapped"),
                "rf_proba": ml_result["rf_proba"],
                "iso_raw_score": ml_result["iso_raw_score"],
            }
            risk_result = requests.post(f"{RISK_API}/score-risk", json=risk_payload).json()

            # 4. Indexation finale
            correlated = {
                "@timestamp": alert["@timestamp"],
                "src_ip": alert.get("src_ip"), "dest_ip": alert.get("dest_ip"),
                "signature": signature,
                "mitre": alert.get("mitre", {}),
                "ml": ml_result, "risk": risk_result,
            }
            
            ES.index(index="correlated-events", document=correlated)
            print(f"     [SUCCESS] Incident indexé (Risque: {risk_result['risk_level']} | Score: {risk_result['risk_score']})")
            
            # 5. On met à jour l'horloge
            last_ts = alert["@timestamp"]

    except Exception as e:
        print(f"[-] Erreur boucle : {e}")
        
    time.sleep(10)