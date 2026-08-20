# Méthodologie d'Évaluation des Risques (Risk Scoring Engine)

## Objectif
Le moteur de *Risk Scoring* du SOC SENTRA a pour but de réduire la "fatigue des alertes" (Alert Fatigue) des analystes de niveau 1 (L1). Plutôt que de traiter chaque événement réseau de manière isolée, le moteur attribue un score dynamique de criticité sur 100 points, basé sur la fusion de quatre signaux distincts : déterministe (IDS), contextuel (MITRE) et probabiliste (Intelligence Artificielle supervisée et non-supervisée).

## Formule de Pondération (Sur 100 Points)

La formule a été calibrée de la manière suivante : **IDS (35%) + RF (30%) + IF (20%) + MITRE (15%) = 100%**.

### 1. Composante Déterministe : Alertes IDS Suricata (Max: 35 pts)
Les règles par signature restent le socle d'un SOC. Une règle déclenchée avec une sévérité haute indique une certitude quasi-absolue de l'activité malveillante.
- **Sévérité 1 (Haute) :** 35 pts
- **Sévérité 2 (Moyenne) :** 23.3 pts
- **Sévérité 3 (Basse) :** 11.6 pts

### 2. Composante IA Supervisée : Random Forest (Max: 30 pts)
Le modèle Random Forest a prouvé son excellente capacité de généralisation sur les attaques connues (F1-score de 0.97 lors de l'entraînement). Son poids est élevé pour confirmer la certitude technique de l'attaque.
- **Calcul :** Probabilité de la classe `ATTACK` (de 0.0 à 1.0) multipliée par 30.

### 3. Composante IA Non-Supervisée : Isolation Forest (Max: 20 pts)
Bien que l'Isolation Forest soit excellent pour identifier des anomalies comportementales ou des attaques Zero-Day, son *rappel* (capacité à ne pas rater des attaques) est structurellement plus faible que le modèle supervisé. Pour éviter de pénaliser le score global avec des Faux Négatifs de l'IF, son poids est volontairement réduit à 20%.
- **Calcul :** Score brut d'anomalie normalisé, multiplié par 20.

### 4. Composante Contextuelle : MITRE ATT&CK (Max: 15 pts)
Toutes les attaques n'ont pas le même impact métier. Un scan de port automatisé représente un risque d'intrusion futur, tandis qu'une attaque par force brute indique une tentative active de compromission.
- **Credential Access :** Poids 1.0 (15 pts)
- **Reconnaissance :** Poids 0.5 (7.5 pts)
- **Unmapped (Inconnu) :** Poids 0.3 (4.5 pts)

## Niveaux d'Escalade SOC (SLA)

Le score total dicte le niveau de priorité de l'incident dans le tableau de bord de l'analyste :

| Score Total | Niveau de Risque | Action Requise (Playbook SOC) |
| :--- | :--- | :--- |
| **80 - 100** | CRITICAL | Isolement réseau immédiat de la machine cible. Escalade L2/L3. |
| **60 - 79** | HIGH | Analyse manuelle prioritaire dans les 15 minutes. |
| **30 - 59** | MEDIUM | Revue quotidienne par un analyste L1. |
| **0 - 29** | LOW | Logué à des fins d'audit. Aucune action immédiate requise. |