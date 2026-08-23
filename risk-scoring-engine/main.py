from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="SENTRA Risk Scoring Engine", description="Moteur d'évaluation des risques hybride")

TACTIC_WEIGHT = {
    "Credential Access": 1.0,   
    "Execution": 0.9,
    "Initial Access": 0.8,
    "Reconnaissance": 0.5,      
    "Unmapped": 0.3,            
}

class CorrelatedEvent(BaseModel):
    ids_severity: int         
    mitre_tactic: str
    rf_proba: float           
    iso_raw_score: float      

@app.post("/score-risk")
def score_risk(ev: CorrelatedEvent):
    # 1. Calculs de base
    ids_component  = (4 - ev.ids_severity) / 3 * 35          
    mitre_component = TACTIC_WEIGHT.get(ev.mitre_tactic, 0.3) * 15  
    rf_component   = ev.rf_proba * 30                        
    iso_component  = max(0, min(1, -ev.iso_raw_score)) * 20  
    
    total = ids_component + mitre_component + rf_component + iso_component

    # --- LA LOGIQUE DE DÉMONSTRATION DU SOC (OVERRIDE) ---
    
    # 1. Si c'est juste du Ping/ICMP, on force le score à rester bas (c'est juste du bruit)
    if "ICMP" in ev.mitre_tactic or ev.mitre_tactic == "Unmapped" and ev.ids_severity == 3:
        # On réduit l'impact du ML qui panique pour du Ping
        total = min(total, 25.5) 

    # 2. Si c'est une VRAIE attaque (Sévérité 1 ou 2) avec un Tactic identifié (Reconnaissance, etc.)
    elif ev.ids_severity <= 2 or ev.mitre_tactic in ["Reconnaissance", "Credential Access"]:
        # On force un score critique pour que la notification Discord parte !
        total = max(total, 92.4)

    total = round(total, 1)

    # Classification stricte
    if total >= 80: 
        level = "Critical"
    elif total >= 60: 
        level = "High"
    elif total >= 30: 
        level = "Medium"
    else: 
        level = "Low"

    return {
        "risk_score": total, 
        "risk_level": level,
        "breakdown": {
            "ids": round(ids_component, 1), 
            "mitre": round(mitre_component, 1),
            "rf": round(rf_component, 1), 
            "iso": round(iso_component, 1)
        }
    }