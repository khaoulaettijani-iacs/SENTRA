# SENTRA — SOC Platform Prototype (IDS/ML)

## Vision
SENTRA est un prototype de plateforme SOC démontrant la détection, l'intégration
SIEM, la corrélation IDS/ML, la priorisation par le risque, l'auditabilité et
le reporting orienté analyste.

## Contexte
Projet de fin d'année (PFA) — ENSA Beni Mellal, Ingénierie d'État IA & Cybersécurité.

## Architecture
Sources de données → Couche d'intégration SIEM → Backend SOC Services →
Stockage et infrastructure → Frontend/Dashboard analyste → Intégrations externes

## Stack technique
- Lab : Kali (attaquant), pfSense (firewall/routeur), Ubuntu Server (DMZ), Ubuntu SOC (SENTRA), VMware Workstation Pro, VMnets séparés
- SIEM : Elasticsearch, Kibana, Filebeat, Suricata
- ML : Random Forest, Isolation Forest (scikit-learn)
- Backend : Python (Correlation Engine, ML Engine, Risk Scoring Engine)
- Stockage : PostgreSQL

## Structure du repo
~~~text
SENTRA/
├── README.md
├── docs/
│   ├── architecture/          # diagrammes, ADRs
│   ├── report-fr/             # rapport en français (chapitres)
│   └── report-en/             # résumé technique anglais
├── infra/
│   ├── docker-compose.yml
│   ├── elk/                   # config Elasticsearch/Kibana
│   └── network/               # schémas réseau, config pfSense exportée
├── ids/
│   └── suricata/               # règles custom
├── backend/
│   ├── correlation_engine/
│   ├── ml_engine/
│   └── scoring_engine/
├── ml/
│   ├── notebooks/
│   └── models/                 # modèles entraînés sauvegardés (.pkl)
├── reporting/
│   └── templates/
└── evidence/                   # captures d'écran, logs horodatés (evidence pack)
~~~