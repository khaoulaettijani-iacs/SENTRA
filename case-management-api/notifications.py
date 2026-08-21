def notify_if_critical(incident: dict):
    return {"email": {"sent": False}, "webhook": {"sent": False}}