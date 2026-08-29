# Architecture & Machine Learning

Ce module centralise les composants d'intelligence artificielle de la plateforme SENTRA, combinant des approches supervisées (Random Forest) et non supervisées (Isolation Forest) pour la détection d'anomalies et la classification des menaces.

## Différence entre les Générations (V1 vs V2)

Le projet intègre une évolution de ses modèles pour s'adapter aux contraintes opérationnelles du laboratoire (flux capturés par Suricata en direct) :

- Modèles V1 (Offline Benchmark - 20 features) :
* Entraînés sur un ensemble large de 20 caractéristiques réseau issues du dataset CICIDS2017.
* Idéal pour l'analyse hors-ligne et l'exploration de performances maximales (bénéficie de la richesse complète des attributs d'origine).

- Modèles V2 Lean (Production Live - 8 features) :
* Réduit à un sous-ensemble strict de 8 features (**Flow Duration**, **Total Fwd Packets**, **Total Backward Packets**, **Total Length of Fwd Packets**, **Total Length of Bwd Packets**, **Flow Bytes/s**, **Flow Packets/s**, **Down/Up Ratio**).
* Parfaitement compatible avec l'extraction de flux en temps réel depuis les sondes Suricata en production, garantissant un couplage direct sans latence de calcul.
---

## Comment réentraîner les modèles

Le script d'automatisation (`train.py`) gère l'ensemble du pipeline, du nettoyage à la sérialisation des modèles v1 et v2.

1. Placez les fichiers CSV du dataset CICIDS2017 (`Tuesday-WorkingHours.pcap_ISCX.csv`, etc.) dans le dossier `ml/data/raw/` (ou laissez le script basculer automatiquement sur l'échantillon réduit dans `ml/data/sample/` si les fichiers bruts sont absents).


2. Exécutez le script d'entraînement depuis la racine du dossier `ml/` :
```bash
python train.py

```


3. Le script va automatiquement :
* Charger et nettoyer les données (suppression des valeurs infinies, des valeurs manquantes et des biais de *data leakage*).

* Entraîner et sauvegarder les modèles **V1** (`random_forest_v1.pkl`, `isolation_forest_v1.pkl`) ainsi que leurs artefacts associés (`scaler.pkl`, `feature_columns.json`).

* Entraîner et sauvegarder les modèles **V2 Lean** (`random_forest_v2_lean.pkl`, `isolation_forest_v2_lean.pkl`) ainsi que leur scaler dédié (`scaler_v2.pkl`) et leurs colonnes associées (`feature_columns_v2.json`) dans le dossier `ml/models/`.

---

## Comment régénérer les figures et graphiques

Les visualisations de performance (matrices de confusion et courbes ROC) sont générées dynamiquement dans les notebooks Jupyter associés. Pour les régénérer :

1. Ouvrez l'environnement de travail Jupyter et exécutez séquentiellement les notebooks de la phase d'apprentissage :
* **`01_preprocessing.ipynb`** : Exécute le prétraitement et met à jour les matrices splittées sur le disque.

* **`02_random_forest.ipynb`** : Entraîne le classifieur, calcule les métriques, affiche et sauvegarde les graphiques de performance du Random Forest.

* **`03_isolation_forest.ipynb`** : Entraîne le modèle non supervisé sur le trafic bénigne, évalue les performances et exporte le tableau récapitulatif comparatif sous `../models/ml-results-comparison.csv`.
2. Pour sauvegarder directement les figures sous forme d'images statiques dans les dossiers de documentation, décommentez les lignes de sauvegarde associées dans les cellules graphiques des notebooks (ex: `plt.savefig(...)`) avant de les relancer.