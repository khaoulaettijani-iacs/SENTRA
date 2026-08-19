"""
Script d'entraînement automatisé du projet SENTRA.
Exécute le prétraitement, entraîne Random Forest et Isolation Forest, 
et sauvegarde les modèles et scalers.
"""

import pandas as pd
import numpy as np
import os
import joblib
import json
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, IsolationForest

def main():
    print("[*] Démarrage du pipeline d'entraînement SENTRA...")
    
    # 1. Chargement
    raw_files = [
        "data/raw/Tuesday-WorkingHours.pcap_ISCX.csv",
        "data/raw/Wednesday-workingHours.pcap_ISCX.csv",
        "data/raw/Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv",
    ]
    
    if not os.path.exists(raw_files[0]):
        print("[!] Fichiers complets introuvables. Utilisation du sample.")
        raw_files = ["data/sample/sample_dataset.csv"]

    print(f"[*] Chargement des données depuis {len(raw_files)} fichier(s)...")
    df = pd.concat([pd.read_csv(f) for f in raw_files], ignore_index=True)
    df.columns = df.columns.str.strip()
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df.dropna(inplace=True)

    # 2. Prétraitement
    print("[*] Prétraitement et sélection des features...")
    leak_cols = ["Flow ID", "Source IP", "Destination IP", "Source Port", "Timestamp"]
    df.drop(columns=[c for c in leak_cols if c in df.columns], inplace=True)
    df["Label_binary"] = df["Label"].apply(lambda x: "BENIGN" if x == "BENIGN" else "ATTACK")

    selected_features = [
        "Flow Duration", "Total Fwd Packets", "Total Backward Packets",
        "Total Length of Fwd Packets", "Total Length of Bwd Packets",
        "Fwd Packet Length Max", "Fwd Packet Length Mean",
        "Bwd Packet Length Max", "Bwd Packet Length Mean",
        "Flow Bytes/s", "Flow Packets/s", "Flow IAT Mean", "Flow IAT Std",
        "Fwd IAT Mean", "Bwd IAT Mean", "SYN Flag Count", "ACK Flag Count", 
        "PSH Flag Count", "Average Packet Size", "Down/Up Ratio",
    ]

    X = df[selected_features]
    y_binary = df["Label_binary"]

    X_train, X_test, y_train, y_test = train_test_split(X, y_binary, test_size=0.25, stratify=y_binary, random_state=42)

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)

    # Sauvegardes préliminaires
    os.makedirs("models", exist_ok=True)
    joblib.dump(scaler, "models/scaler.pkl")
    with open("models/feature_columns.json", "w") as f:
        json.dump(selected_features, f)

    # 3. Entraînement Random Forest
    print("[*] Entraînement du Random Forest (Supervisé)...")
    rf = RandomForestClassifier(n_estimators=200, class_weight="balanced", random_state=42, n_jobs=-1)
    rf.fit(X_train, y_train)
    joblib.dump(rf, "models/random_forest_v1.pkl")

    # 4. Entraînement Isolation Forest
    print("[*] Entraînement de l'Isolation Forest (Non-Supervisé)...")
    X_train_benign = X_train_scaled[y_train.values == "BENIGN"]
    iso = IsolationForest(n_estimators=200, contamination=0.05, random_state=42, n_jobs=-1)
    iso.fit(X_train_benign)
    joblib.dump(iso, "models/isolation_forest_v1.pkl")

    print("[+] Pipeline terminé avec succès. Tous les modèles sont sauvegardés dans ml/models/.")

if __name__ == "__main__":
    main()