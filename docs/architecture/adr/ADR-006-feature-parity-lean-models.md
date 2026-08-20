# ADR-006 : Parité des Caractéristiques et Modèles "Lean" pour la Production (Train/Serve Skew)

## Contexte
Lors du passage de la phase de validation académique (Chapitre 4) à l'intégration au sein de l'architecture SOC en temps réel (Chapitre 5), une disparité technique majeure a été identifiée entre les données d'entraînement (dataset CICIDS2017) et les données générées en direct par le moteur IDS Suricata dans notre infrastructure.

Les modèles initiaux (version "v1") ont été entraînés sur 20 caractéristiques (features) statistiques complexes issues de CICIDS2017, telles que l'écart-type des temps d'inter-arrivée (`Flow IAT Std`) ou le comptage détaillé des drapeaux TCP (`PSH Flag Count`). Cependant, l'exportation réseau standard de Suricata (format `eve.json` de type `flow`) ne calcule pas nativement ces statistiques avancées par session de manière suffisamment granulaire pour une inférence en temps réel. 

Utiliser les modèles v1 tels quels en production créerait un "Train/Serve Skew" (décalage entraînement/inférence) : le modèle recevrait des requêtes avec des features manquantes (remplies par des zéros), ce qui fausserait complètement les prédictions d'anomalies.

## Décision
Plutôt que de développer un extracteur de caractéristiques (Feature Extractor) complexe et gourmand en ressources pour intercepter et analyser les PCAP en direct, nous avons opté pour une approche MLOps de "Feature Parity" (Parité des Caractéristiques).

Nous avons décidé de maintenir **deux versions distinctes** de nos modèles de Machine Learning :
1. **Modèles v1 (Benchmark Offline) :** Entraînés sur les 20 features originelles de CICIDS2017. Ils servent de référence académique (Baseline) pour documenter les performances maximales théoriques dans la phase de recherche du projet.
2. **Modèles v2 "Lean" (Production SOC) :** Entraînés sur un sous-ensemble strict de 8 features, sélectionnées car elles sont mathématiquement extractibles à la volée depuis les événements `flow` natifs de Suricata. Ce sont ces modèles qui sont déployés dans le conteneur `backend-api`.

### Mapping des Features "Lean" (v2) :
| Feature Entraînement v2 (CICIDS2017) | Champ Source Production (Suricata eve.json) | Méthode d'Extraction (Correlation Engine) |
| :--- | :--- | :--- |
| `Flow Duration` | `flow.age` | `max(flow.age, 1)` (Conversion et protection div/0) |
| `Total Fwd Packets` | `flow.pkts_toserver` | Extraction directe |
| `Total Backward Packets` | `flow.pkts_toclient` | Extraction directe |
| `Total Length of Fwd Packets` | `flow.bytes_toserver` | Extraction directe |
| `Total Length of Bwd Packets` | `flow.bytes_toclient` | Extraction directe |
| `Flow Bytes/s` | `flow.bytes_*` + `flow.age` | `(bytes_toserver + bytes_toclient) / age` |
| `Flow Packets/s` | `flow.pkts_*` + `flow.age` | `(pkts_toserver + pkts_toclient) / age` |
| `Down/Up Ratio` | `flow.bytes_*` | `bytes_toclient / bytes_toserver` |

## Conséquences

### Avantages
*   **Élimination du "Train/Serve Skew" :** Le modèle d'inférence en production reçoit exactement la même structure de données que lors de son entraînement, garantissant la fiabilité des prédictions.
*   **Haute Performance (Low Latency) :** Le payload JSON envoyé à l'API ML est extrêmement léger, et le calcul des dérivées (Bytes/s, Packets/s) par le `correlation-engine` Python s'effectue en mémoire via de simples divisions, sans surcharger la CPU.
*   **Stabilité du Pipeline :** Nous restons dépendants uniquement du moteur robuste de Suricata pour la capture des flux, sans introduire de point de défaillance supplémentaire (SPOF) via un analyseur PCAP tiers.

### Inconvénients (Risques acceptés)
*   **Baisse de la dimensionnalité :** L'absence des caractéristiques basées sur le temps (IAT) et des drapeaux TCP réduit mathématiquement la "vision" comportementale du modèle, particulièrement face à des attaques très lentes (Low and Slow) ou des scans furtifs (Half-open SYN). 
*   **Atténuation du risque :** Cette concession est compensée par notre architecture de "Risk Scoring Engine". L'IA n'est pas l'unique décideur ; elle est fusionnée au score déterministe IDS et au contexte MITRE ATT&CK. Même si le modèle ML Lean rate une anomalie fine, la signature Suricata garantit la détection.