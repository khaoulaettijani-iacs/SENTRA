import os
import requests

WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

def send_webhook(incident: dict):
    if not WEBHOOK_URL:
        return {"sent": False, "reason": "webhook non configuré"}
        
    # Extraction des données d'enrichissement CTI
    enrichment = incident.get("enrichment", {})
    geo = enrichment.get("geo", {}).get("country", "Inconnu")
    abuse = enrichment.get("reputation", {}).get("abuse_confidence_score", "N/A")
    
    message = (
        f"🚨 **ALERTE {incident['risk_level'].upper()}** (Score: {incident['risk_score']})\n"
        f"**Source :** `{incident['src_ip']}` 🌍 {geo} | 🛡️ AbuseIPDB: {abuse}%\n"
        f"**Cible :** `{incident['dest_ip']}`\n"
        f"**Technique :** {incident['mitre_technique_id']} - {incident['mitre_technique_name']}"
    )
    
    payload = {"content": message}
    try:
        r = requests.post(WEBHOOK_URL, json=payload, timeout=5)
        return {"sent": r.status_code < 300}
    except Exception as e:
        return {"sent": False, "reason": str(e)}

def notify_if_critical(incident: dict):
    # Déclenche l'alerte uniquement pour les risques élevés ou critiques
    if incident.get("risk_level") in ("Critical", "High"):
        return {
            "email": {"sent": False, "reason": "désactivé"},
            "webhook": send_webhook(incident)
        }
    return {
        "email": {"sent": False, "reason": "risque insuffisant"},
        "webhook": {"sent": False, "reason": "risque insuffisant"}
    }