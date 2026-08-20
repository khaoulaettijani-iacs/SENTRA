from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="SENTRA Risk Scoring Engine", description="Moteur d'évaluation des risques hybride (IDS + MITRE + ML)")

TACTIC_WEIGHT = {
    "Credential Access": 1.0,   # Étape critique (Impact direct)
    "Execution": 0.9,
    "Initial Access": 0.8,
    "Reconnaissance": 0.5,      # Bruit de fond d'internet
    "Unmapped": 0.3,            # Règle ET Open inconnue
}

class CorrelatedEvent(BaseModel):
    ids_severity: int         # 1 (Haute) à 3 (Basse) - Convention Suricata
    mitre_tactic: str
    rf_proba: float           # 0.0 à 1.0 (Probabilité Random Forest)
    iso_raw_score: float      # Score brut Isolation Forest (généralement négatif pour les anomalies)

@app.post("/score-risk")
def score_risk(ev: CorrelatedEvent):
    # 1. Composante IDS (Max: 35 points)
    # Suricata : 1 = Haute, 2 = Moyenne, 3 = Basse
    ids_component  = (4 - ev.ids_severity) / 3 * 35          
    
    # 2. Composante MITRE (Max: 15 points)
    mitre_component = TACTIC_WEIGHT.get(ev.mitre_tactic, 0.3) * 15  
    
    # 3. Composante Random Forest (Max: 30 points)
    rf_component   = ev.rf_proba * 30                        
    
    # 4. Composante Isolation Forest (Max: 20 points)
    # On inverse le score négatif. S'il est très anormal (ex: -0.8), on limite entre 0 et 1.
    iso_component  = max(0, min(1, -ev.iso_raw_score)) * 20  

    # Calcul du score total
    total = round(ids_component + mitre_component + rf_component + iso_component, 1)

    # Classification par niveaux
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