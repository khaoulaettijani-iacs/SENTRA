# ADR-003 : Contournement de la limitation Syslog natif pfSense via le mode Filestore et Syslog-ng

L'ingestion initiale des alertes Suricata (format EVE JSON) reposait sur le module Syslog natif de pfSense. Lors des phases de test de charge et de génération d'alertes (scans Nmap, attaques web), une perte de données et des erreurs de parsing récurrentes ont été constatées dans le pipeline Logstash. 

L'investigation a démontré que le démon syslog natif de pfSense/FreeBSD obéit strictement à la norme RFC5424. Les logs EVE de Suricata étant des objets JSON riches contenant des métadonnées et des payloads volumineux, ils dépassaient régulièrement la taille limite des datagrammes du syslog natif, entraînant une troncature silencieuse et une altération de la structure JSON.

Pour fiabiliser la collecte des alertes NIDS (prérequis strict pour alimenter proprement le moteur de corrélation et de Machine Learning du SOC) :
1. **Abandon de l'export Syslog natif** de pfSense pour les alertes Suricata.
2. **Activation du mode Filestore** : Suricata écrit ses événements en local sous forme de fichiers `eve.json` bruts dans `/var/log/suricata`.
3. **Installation du paquet tiers `syslog-ng`** sur le pare-feu pfSense pour assurer un suivi dynamique et propre de ces fichiers de logs.

## Conséquences
* **Positif :** Intégrité absolue des logs EVE JSON, absence de troncature, et simplification drastique du code de parsing côté Logstash.
* **Négatif :** Dépendance à l'installation d'un paquet additionnel (`syslog-ng`) sur le routeur pfSense.