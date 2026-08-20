#!/usr/bin/env python3
"""
Script d'entraînement automatisé du projet SENTRA.
- Phase 1 : Modèles v1 (Offline Benchmark, 20 features)
- Phase 2 : Modèles v2 Lean (Production Live, 8 features compatibles Suricata)
"""

import pandas as pd
import numpy as np
import os
import joblib
import json
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, IsolationForest

# Détection automatique du dossier 'ml' où se trouve ce script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")
DATA_DIR = os.path.join(BASE_DIR, "data")

def load_and_clean_data():
    """Charge le dataset CICIDS et applique le nettoyage de base."""
    print("[*] Chargement des données...")
    
    raw_files = [
        os.path.join(DATA_DIR, "raw", "Tuesday-WorkingHours.pcap_ISCX.csv"),
        os.path.join(DATA_DIR, "raw", "Wednesday-workingHours.pcap_ISCX.csv"),
        os.path.join(DATA_DIR, "raw", "Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv"),
    ]
    
    if not os.path.exists(raw_files[0]):
        print("[!] Fichiers complets introuvables. Utilisation du sample.")
        raw_files = [os.path.join(DATA_DIR, "sample", "sample_dataset.csv")]

    df = pd.concat([pd.read_csv(f) for f in raw_files], ignore_index=True)
    df.columns = df.columns.str.strip()
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df.dropna(inplace=True)

    # Retrait des colonnes de triche et création du label binaire
    leak_cols = ["Flow ID", "Source IP", "Destination IP", "Source Port", "Timestamp"]
    df.drop(columns=[c for c in leak_cols if c in df.columns], inplace=True)
    df["Label_binary"] = df["Label"].apply(lambda x: "BENIGN" if x == "BENIGN" else "ATTACK")
    
    return df

def train_v1_models(df):
    """Entraîne les modèles V1 (Benchmark - 20 features)."""
    print("\n--- Entraînement Modèles v1 (Benchmark Offline) ---")
    
    selected_features_v1 = [
        "Flow Duration", "Total Fwd Packets", "Total Backward Packets",
        "Total Length of Fwd Packets", "Total Length of Bwd Packets",
        "Fwd Packet Length Max", "Fwd Packet Length Mean",
        "Bwd Packet Length Max", "Bwd Packet Length Mean",
        "Flow Bytes/s", "Flow Packets/s", "Flow IAT Mean", "Flow IAT Std",
        "Fwd IAT Mean", "Bwd IAT Mean", "SYN Flag Count", "ACK Flag Count", 
        "PSH Flag Count", "Average Packet Size", "Down/Up Ratio",
    ]

    X = df[selected_features_v1]
    y_binary = df["Label_binary"]

    X_train, X_test, y_train, y_test = train_test_split(X, y_binary, test_size=0.25, stratify=y_binary, random_state=42)

    scaler_v1 = StandardScaler()
    X_train_scaled = scaler_v1.fit_transform(X_train)

    os.makedirs(MODELS_DIR, exist_ok=True)
    
    joblib.dump(scaler_v1, os.path.join(MODELS_DIR, "scaler.pkl"))
    with open(os.path.join(MODELS_DIR, "feature_columns.json"), "w") as f:
        json.dump(selected_features_v1, f)

    print("[*] Entraînement Random Forest v1...")
    rf = RandomForestClassifier(n_estimators=200, class_weight="balanced", random_state=42, n_jobs=-1)
    rf.fit(X_train, y_train)
    joblib.dump(rf, os.path.join(MODELS_DIR, "random_forest_v1.pkl"))

    print("[*] Entraînement Isolation Forest v1...")
    X_train_benign = X_train_scaled[y_train.values == "BENIGN"]
    iso = IsolationForest(n_estimators=200, contamination=0.05, random_state=42, n_jobs=-1)
    iso.fit(X_train_benign)
    joblib.dump(iso, os.path.join(MODELS_DIR, "isolation_forest_v1.pkl"))


def train_lean_models(df):
    """Entraîne les modèles V2 Lean (Production Live - 8 features compatibles Suricata)."""
    print("\n--- Entraînement Modèles v2 Lean (Production Live) ---")
    
    selected_features_v2 = [
        "Flow Duration", 
        "Total Fwd Packets", 
        "Total Backward Packets",
        "Total Length of Fwd Packets", 
        "Total Length of Bwd Packets",
        "Flow Bytes/s", 
        "Flow Packets/s", 
        "Down/Up Ratio"
    ]

    # Pour éviter les erreurs avec certaines colonnes générées pendant l'extraction Suricata
    # on s'assure qu'elles existent dans le DataFrame
    X_v2 = df[selected_features_v2]
    y_binary = df["Label_binary"]

    X_train_v2, X_test_v2, y_train_v2, y_test_v2 = train_test_split(X_v2, y_binary, test_size=0.25, stratify=y_binary, random_state=42)

    scaler_v2 = StandardScaler()
    X_train_scaled_v2 = scaler_v2.fit_transform(X_train_v2)

    joblib.dump(scaler_v2, os.path.join(MODELS_DIR, "scaler_v2.pkl"))
    with open(os.path.join(MODELS_DIR, "feature_columns_v2.json"), "w") as f:
        json.dump(selected_features_v2, f)

    print("[*] Entraînement Random Forest v2 Lean...")
    rf_v2 = RandomForestClassifier(n_estimators=200, class_weight="balanced", random_state=42, n_jobs=-1)
    rf_v2.fit(X_train_v2, y_train_v2)
    joblib.dump(rf_v2, os.path.join(MODELS_DIR, "random_forest_v2_lean.pkl"))

    print("[*] Entraînement Isolation Forest v2 Lean...")
    X_train_benign_v2 = X_train_scaled_v2[y_train_v2.values == "BENIGN"]
    iso_v2 = IsolationForest(n_estimators=200, contamination=0.05, random_state=42, n_jobs=-1)
    iso_v2.fit(X_train_benign_v2)
    joblib.dump(iso_v2, os.path.join(MODELS_DIR, "isolation_forest_v2_lean.pkl"))

def main():
    print("=====================================================")
    print(" Démarrage du pipeline d'entraînement SENTRA ML")
    print("=====================================================")
    
    df = load_and_clean_data()
    train_v1_models(df)
    train_lean_models(df)
    
    print("\n[+] Pipeline terminé avec succès. Tous les modèles (v1 et v2) sont sauvegardés dans ml/models/.")

if __name__ == "__main__":
    main()