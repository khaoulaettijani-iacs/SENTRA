import time
import os
import requests
from elasticsearch import Elasticsearch

ES_HOST = os.environ.get("ES_HOST", "http://elasticsearch:9200")
ML_API = os.environ.get("ML_API", "http://backend-api:8000")
RISK_API = os.environ.get("RISK_API", "http://risk-scoring-engine:8000")
# Ajout de l'URL vers ton API Case Management
CASE_API_URL = os.environ.get("CASE_API_URL", "http://case-management-api:8000/incidents")

print(f"[*] Démarrage du Correlation Engine SENTRA...")
print(f"[*] ES_HOST: {ES_HOST} | ML_API: {ML_API} | RISK_API: {RISK_API} | CASE_API: {CASE_API_URL}")

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
    """Extrait les 8 features ML avec des valeurs de secours réalistes (évite le Train/Serve Skew)"""
    flow = document.get("flow", {})
    
    # Sécurisation des valeurs par défaut pour éviter de tromper le ML avec des zéros absolus
    age = max(float(flow.get("age", 1.0)), 0.1) # Pas de division par zéro
    bts = float(flow.get("bytes_toserver", 64.0)) # Au moins 64 octets (1 paquet IP basique)
    btc = float(flow.get("bytes_toclient", 0.0))
    pts = float(flow.get("pkts_toserver", 1.0))   # Au moins 1 paquet envoyé
    ptc = float(flow.get("pkts_toclient", 0.0))
    
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
                    print("    [i] Utilisation du snapshot réseau en temps réel.")
                    target_data = alert
                else:
                    print("    [!] Aucun contexte réseau. Alerte ignorée.")
                    last_ts = alert["@timestamp"]
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

            # 4. Indexation finale dans Elasticsearch
            correlated = {
                "@timestamp": alert["@timestamp"],
                "src_ip": alert.get("src_ip"), "dest_ip": alert.get("dest_ip"),
                "signature": signature,
                "mitre": alert.get("mitre", {}),
                "ml": ml_result, "risk": risk_result,
            }
            
            ES.index(index="correlated-events", document=correlated)
            print(f"    [SUCCESS] Incident indexé (Risque: {risk_result['risk_level']} | Score: {risk_result['risk_score']})")
            
            # --- 4.bis : PUSH VERS LE CASE MANAGEMENT & NOTIFICATIONS ---
            # On prépare le payload attendu par ton API Case Management
            case_payload = {
                "correlated_event_id": hit["_id"],  # Utilisation de l'ID unique de l'alerte ES comme identifiant
                "src_ip": alert.get("src_ip", "0.0.0.0"),
                "dest_ip": alert.get("dest_ip", "0.0.0.0"),
                "signature": signature,
                "mitre_tactic": alert.get("mitre", {}).get("tactic", "Unmapped"),
                "mitre_technique_id": alert.get("mitre", {}).get("technique_id", "T0000"),
                "mitre_technique_name": alert.get("mitre", {}).get("technique_name", "Unknown Technique"),
                "risk_score": float(risk_result.get("risk_score", 0.0)),
                "risk_level": risk_result.get("risk_level", "Low"),
                "enrichment": {}
            }
            
            try:
                api_resp = requests.post(CASE_API_URL, json=case_payload, timeout=5)
                if api_resp.status_code == 200:
                    print(f"    [+] Transmis à l'API Case Management avec succès !")
                else:
                    print(f"    [-] Erreur API Case Management ({api_resp.status_code}): {api_resp.text}")
            except Exception as api_err:
                print(f"    [-] Impossible de contacter l'API Case Management : {api_err}")
            # -------------------------------------------------------------

            # 5. On met à jour l'horloge
            last_ts = alert["@timestamp"]

    except Exception as e:
        print(f"[-] Erreur boucle : {e}")
        
    time.sleep(10)