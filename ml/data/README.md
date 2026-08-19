# Référentiel de Données ML (Dataset)

> Les fichiers de données bruts (.csv) ne sont pas inclus dans ce dépôt en raison de leur taille (plusieurs Go). Seul un échantillon (`sample/sample_dataset.csv`) est fourni pour tester le pipeline.

## Dataset Utilisé : CICIDS2017
Pour entraîner les modèles de Machine Learning du projet SENTRA, nous utilisons le dataset académique **CICIDS2017** (Canadian Institute for Cybersecurity), réputé pour sa diversité d'attaques et la fiabilité de ses labels.

### Instructions de téléchargement
1. Rendez-vous sur la page Kaggle du dataset : [Machine Learning Security Dataset - CICIDS2017](https://www.kaggle.com/datasets/cicdataset/cicids2017)
2. Téléchargez l'archive complète.
3. Extrayez **uniquement** les 3 fichiers suivants et placez-les dans le dossier `ml/data/raw/` :
   - `Tuesday-WorkingHours.pcap_ISCX.csv` (Trafic normal, Bruteforce FTP/SSH)
   - `Wednesday-workingHours.pcap_ISCX.csv` (Trafic normal, DoS, Heartbleed)
   - `Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv` (Trafic normal, PortScan)

### Structure attendue
```text
ml/data/
├── raw/
│   ├── Tuesday-WorkingHours.pcap_ISCX.csv
│   ├── Wednesday-workingHours.pcap_ISCX.csv
│   └── Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv
├── sample/
│   └── sample_dataset.csv
└── README.md
```
> Note : Le dossier raw/ est ignoré par Git via le fichier .gitignore.