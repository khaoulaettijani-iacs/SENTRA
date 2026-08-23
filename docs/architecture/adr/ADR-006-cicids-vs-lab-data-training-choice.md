# ADR-005 : Stratégie d'Entraînement des Modèles ML (CICIDS2017 & Isolation Forest)

## Contexte
Pour la phase d'Intelligence Artificielle du projet SENTRA, nous devions définir (1) la source de données pour l'entraînement des modèles et (2) la méthodologie d'apprentissage pour la détection d'anomalies (Isolation Forest).

## Décisions

### 1. Utilisation du dataset CICIDS2017 (vs. Données générées en Lab)
Nous avons choisi d'entraîner nos modèles sur le dataset académique externe CICIDS2017 plutôt que sur les données générées par nos propres scripts d'attaque dans le laboratoire (Kali -> SOC).
*   **Justification :** Un modèle d'apprentissage supervisé (Random Forest) nécessite un volume massif de données et une "Ground Truth" (étiquetage) parfaite pour généraliser. Nos scripts génèrent quelques milliers de logs avec un risque de biais lié à notre propre infrastructure. CICIDS2017 offre plus de 2,5 millions de flux réseau pré-calculés, couvrant une dizaine de familles d'attaques avec une précision académique. Les données du lab serviront de jeu de test ultime "en conditions réelles" (Inference) pour valider la robustesse des modèles face à un environnement nouveau.

### 2. Entraînement de l'Isolation Forest sur le trafic BENIGN uniquement
Contrairement au Random Forest qui reçoit des exemples d'attaques, nous avons décidé de filtrer le dataset d'entraînement pour ne fournir **que** du trafic normal (`BENIGN`) à l'Isolation Forest.
*   **Justification :** C'est l'essence même de la détection d'anomalies (Non-Supervisé). En forçant l'algorithme à modéliser exclusivement le périmètre de la "normalité", il devient capable de flaguer toute déviation comme une anomalie, qu'il s'agisse d'un scan Nmap connu ou d'une vulnérabilité Zero-Day jamais vue. Cela rend l'architecture hybride du SOC beaucoup plus résiliente.

## Conséquences
- **Avantages :** Gain de temps sur l'étiquetage, validation des modèles, complémentarité parfaite entre détection par signature ML (RF) et détection comportementale (IF).
- **Inconvénients (Risque) :** "Domain Shift". Le réseau du dataset CICIDS2017 n'a pas exactement la même topologie que notre lab. Les modèles devront prouver leur capacité à généraliser lors de la phase de détection en temps réel.