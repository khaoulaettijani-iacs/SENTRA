# ADR 008 : Choix de la stack ELK vs Splunk/Graylog pour le SIEM

Le projet SENTRA nécessite un moteur de stockage et de recherche capable d'ingérer des logs réseau bruts (Filebeat) et des alertes de sécurité (Suricata EVE JSON) en temps réel, afin de les mettre à disposition du moteur de corrélation Python.

Nous avons choisi d'utiliser la stack **Elastic (Elasticsearch, Logstash, Kibana)** en version Dockerisée (Open Source), plutôt que Splunk ou Graylog pour plusieurs raisons: 

1.  **Écosystème natif :** Logstash dispose d'une intégration parfaite avec Suricata et permet de manipuler des objets JSON complexes sans configuration lourde.
2.  **Coût et Licence :** Splunk est une solution propriétaire dont la version gratuite est limitée à 500 Mo d'indexation par jour. ELK offre une scalabilité sans contrainte de licence pour un projet académique.
3.  **Flexibilité de requêtage (API REST) :** Le moteur de corrélation en Python (FastAPI/Pandas) doit interroger massivement la base de données. L'API REST d'Elasticsearch est extrêmement rapide et documentée pour ce type de charge de travail (agrégations, filtres temporels).
4.  **Visualisation :** Kibana permet de créer des tableaux de bord dynamiques très rapidement sans avoir à coder une interface web spécifique pour le SOC.

## Conséquences
*   **Positif :** Déploiement simplifié via Docker Compose, requêtage rapide par les microservices Python.
*   **Négatif :** Elasticsearch consomme beaucoup de RAM (Java Heap). Il a fallu limiter l'utilisation mémoire (`-Xms1g -Xmx1g`) dans le `docker-compose.yml` pour éviter que la VM SOC (Ubuntu) ne sature.