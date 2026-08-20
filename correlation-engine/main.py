import time
import os
import requests
from elasticsearch import Elasticsearch

# ... (les définitions de ES_HOST, ML_API, RISK_API, find_flow, extract_features restent identiques) ...

print(f"[*] Démarrage du Correlation Engine SENTRA...")

ES = Elasticsearch(ES_HOST)

# --- NOUVELLE LOGIQUE D'INITIALISATION DU TIMESTAMP ---
# On va chercher le tout dernier timestamp enregistré dans Suricata pour commencer à écouter à partir de là
print("[*] Initialisation de la ligne de base temporelle...")
try:
    init_query = ES.search(
        index="suricata-*", 
        query={"term": {"event_type": "alert"}}, 
        sort=[{"@timestamp": "desc"}], # On trie du plus récent au plus ancien
        size=1 # On ne prend que le tout dernier
    )
    if init_query["hits"]["hits"]:
        last_ts = init_query["hits"]["hits"][0]["_source"]["@timestamp"]
        print(f"[+] Ligne de base établie à l'alerte la plus récente : {last_ts}")
    else:
        # S'il n'y a absolument aucune alerte dans la base, on commence très large
        last_ts = "now-24h"
        print("[!] Aucune alerte trouvée dans l'historique. Début de la recherche à : now-24h")
except Exception as e:
    print(f"[-] Erreur lors de l'initialisation : {e}")
    last_ts = "now-2m"

print("[+] Moteur en écoute (Polling: 10s)...")

while True:
    try:
        # On demande STRICTEMENT ce qui est arrivé APRES last_ts
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

            # Appel aux APIs
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
            
            # Mise à jour du last_ts pour le prochain cycle
            # Cela garantit qu'on ne traite jamais deux fois la même alerte
            last_ts = alert["@timestamp"]

    except Exception as e:
        print(f"[-] Erreur boucle : {e}")
        
    time.sleep(10)