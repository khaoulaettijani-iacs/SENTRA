# Configuration EVE JSON (Suricata NIDS)

Ce document détaille la configuration d'export des événements générés par le moteur Suricata déployé sur pfSense.

## Modules EVE Activés
Afin de maintenir un équilibre entre la visibilité nécessaire pour la détection des attaques (scénarios Nmap, Brute-force SSH, attaques Web) et la consommation de stockage, les sous-modules suivants sont activés pour le MVP :
* **Alert :** Indispensable. Exporte les métadonnées de toute signature IDS déclenchée.
* **Flow / Netflow :** Exporte les statistiques de session TCP/UDP. Utile pour le moteur de Machine Learning afin de détecter des anomalies volumétriques.
* Les modules HTTP, DNS et TLS sont activés pour des investigations approfondies.

## Choix du mode d'export : Filestore vs Syslog Natif
**L'option "Syslog" native de l'interface pfSense n'est pas utilisée.**

*   **Problème du Syslog natif :** Le démon syslog natif de FreeBSD obéit strictement à la norme RFC5424 qui limite la taille des datagrammes UDP. Les logs EVE de Suricata étant des objets JSON complexes contenant des payloads réseau, ils dépassent régulièrement cette limite, entraînant une troncature silencieuse et des erreurs de parsing JSON côté Logstash.
*   **Solution retenue (Filestore) :** Suricata est configuré en mode **Filestore**. Les événements sont écrits localement en JSON pur dans `/var/log/suricata/*/eve.json`. C'est le composant `syslog-ng` (via TCP) qui prend ensuite le relais pour expédier ce fichier vers le SOC, garantissant l'intégrité absolue de la donnée.