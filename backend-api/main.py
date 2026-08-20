from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd

app = FastAPI(title="SENTRA ML API", description="API servant les modèles de détection d'intrusions")

# Chargement des modèles depuis le volume monté
rf = joblib.load("models/random_forest_v2_lean.pkl")
iso = joblib.load("models/isolation_forest_v2_lean.pkl")
scaler = joblib.load("models/scaler_v2.pkl")

# Features d'entraînement v2
FEATURES = [
    "Flow Duration", "Total Fwd Packets", "Total Backward Packets",
    "Total Length of Fwd Packets", "Total Length of Bwd Packets",
    "Flow Bytes/s", "Flow Packets/s", "Down/Up Ratio"
]

class FlowFeatures(BaseModel):
    flow_duration: float
    total_fwd_packets: float
    total_bwd_packets: float
    total_len_fwd: float
    total_len_bwd: float
    flow_bytes_per_sec: float
    flow_packets_per_sec: float
    down_up_ratio: float

@app.post("/score")
def score(features: FlowFeatures):
    # Mapping exact entre les noms Pydantic (snake_case) et les noms du modèle (Title Case)
    data = {
        "Flow Duration": features.flow_duration,
        "Total Fwd Packets": features.total_fwd_packets,
        "Total Backward Packets": features.total_bwd_packets,
        "Total Length of Fwd Packets": features.total_len_fwd,
        "Total Length of Bwd Packets": features.total_len_bwd,
        "Flow Bytes/s": features.flow_bytes_per_sec,
        "Flow Packets/s": features.flow_packets_per_sec,
        "Down/Up Ratio": features.down_up_ratio
    }
    
    # Création du DataFrame 
    X = pd.DataFrame([data])[FEATURES]
    X_scaled = scaler.transform(X)

    # Prédiction Random Forest (Supervisé)
    # L'index 0 correspond à "ATTACK", l'index 1 à "BENIGN"
    rf_proba = float(rf.predict_proba(X)[0][0])
    rf_label = "ATTACK" if rf_proba >= 0.5 else "BENIGN"

    # Prédiction Isolation Forest (Non-Supervisé)
    iso_raw = float(iso.decision_function(X_scaled)[0])   # Plus c'est négatif, plus c'est anormal
    iso_label = "ATTACK" if iso.predict(X_scaled)[0] == -1 else "BENIGN"

    return {
        "rf_label": rf_label, 
        "rf_proba": rf_proba,
        "iso_label": iso_label, 
        "iso_raw_score": iso_raw
    }