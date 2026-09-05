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
    
    # 2. Somme réelle sans forçage "démo"
    total = ids_component + mitre_component + rf_component + iso_component

    # On s'assure juste que le total reste logiquement entre 0 et 100
    total = max(0.0, min(100.0, round(total, 1)))

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