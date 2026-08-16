# Configuration et Règles Suricata (NIDS)

Ce répertoire contient la configuration de déploiement de Suricata ainsi que les règles de détection personnalisées développées pour la plateforme SENTRA.

## Stratégie de Détection Hybride
Le moteur IDS s'appuie sur une approche à deux niveaux :
1. **Règles Communautaires (ET Open) :** Couverture large contre les menaces connues (`scan.rules`, `web_specific_apps.rules`, etc.).
2. **Règles Personnalisées (Custom Rules) :** Signatures spécifiques développées pour intercepter les scénarios d'attaques ciblés de notre laboratoire (ex: Scan Xmas furtifs, énumération agressive de répertoires web).

## Convention de Nommage et SID
Toutes les règles personnalisées SENTRA (stockées dans `rules/custom.rules`) respectent les conventions suivantes :
* **Préfixe du message (msg) :** Toujours préfixé par `SENTRA CUSTOM` pour un filtrage immédiat dans les dashboards du SOC.
* **Plage de SID (Signature ID) :** Utilisation stricte de la plage `9000000+`. Les plages inférieures à 1 000 000 et 2 000 000+ sont réservées aux règles officielles (Emerging Threats, Snort VRT, Community). Réserver la plage 9M+ garantit l'absence totale de collision lors des mises à jour automatiques des jeux de règles standards.