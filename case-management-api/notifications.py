import os, smtplib, requests
from email.mime.text import MIMEText

SMTP_HOST = os.environ.get("SMTP_HOST")
SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))
SMTP_USER = os.environ.get("SMTP_USER")
SMTP_PASS = os.environ.get("SMTP_PASS")
NOTIFY_EMAIL_TO = os.environ.get("NOTIFY_EMAIL_TO")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

def send_email(incident: dict):
    if not all([SMTP_HOST, SMTP_USER, SMTP_PASS, NOTIFY_EMAIL_TO]):
        return {"sent": False, "reason": "SMTP non configuré"}
    body = (f"Incident {incident['risk_level']} (score {incident['risk_score']})\n"
            f"{incident['src_ip']} -> {incident['dest_ip']}\n"
            f"Signature: {incident['signature']}\n"
            f"MITRE: {incident['mitre_technique_id']} - {incident['mitre_technique_name']}\n"
            f"ID incident: {incident['id']}")
    msg = MIMEText(body)
    msg["Subject"] = f"[SENTRA] Incident {incident['risk_level']} détecté"
    msg["From"], msg["To"] = SMTP_USER, NOTIFY_EMAIL_TO
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
            s.starttls(); s.login(SMTP_USER, SMTP_PASS); s.send_message(msg)
        return {"sent": True}
    except Exception as e:
        return {"sent": False, "reason": str(e)}

def send_webhook(incident: dict):
    if not WEBHOOK_URL:
        return {"sent": False, "reason": "webhook non configuré"}
    payload = {"content": f"🚨 {incident['risk_level']} ({incident['risk_score']}) — "
                           f"{incident['src_ip']} → {incident['dest_ip']} — "
                           f"{incident['mitre_technique_id']}"}
    try:
        r = requests.post(WEBHOOK_URL, json=payload, timeout=5)
        return {"sent": r.status_code < 300}
    except Exception as e:
        return {"sent": False, "reason": str(e)}

def notify_if_critical(incident: dict):
    # Déclenche l'alerte uniquement pour les risques élevés
    if incident.get("risk_level") in ("Critical", "High"):
        return {"email": send_email(incident), "webhook": send_webhook(incident)}
    return {"email": {"sent": False, "reason": "risque insuffisant"},
            "webhook": {"sent": False, "reason": "risque insuffisant"}}