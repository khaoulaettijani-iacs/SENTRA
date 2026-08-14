# ADR-005 : Remplacement du Syslog natif UDP par syslog-ng via TCP pour l'ingestion Suricata

## Contexte et Problème
Lors de la Phase 2 d'ingestion des logs, le module Suricata de pfSense était configuré pour envoyer ses événements (EVE JSON) directement via le démon syslog natif de FreeBSD en UDP (port 5000). 
Il a été constaté une perte totale des logs d'alertes dans le SIEM. L'investigation a révélé que FreeBSD applique strictement la limite de la norme RFC5424 sur la longueur des messages syslog. Les payloads EVE JSON étant souvent volumineux (contenant des métadonnées HTTP/TLS, payloads réseau), ils étaient tronqués ou corrompus avant même d'atteindre Logstash, provoquant des erreurs de parsing ou des rejets silencieux.

## Décision
Pour garantir l'intégrité absolue de la donnée (critique pour la fiabilité du futur moteur de Machine Learning) :
1. **Désactivation du Syslog Suricata :** Suricata est désormais configuré pour écrire ses événements EVE localement dans un fichier (`/var/log/suricata/*/eve.json`).
2. **Déploiement de syslog-ng :** Utilisation du package `syslog-ng` sur pfSense pour lire (tail) ce fichier en continu.
3. **Transport TCP et pureté du format :** `syslog-ng` expédie les logs vers Logstash via TCP (garantie de livraison) en utilisant le template `$MSG\n`. Cela supprime l'en-tête syslog classique, livrant un JSON pur directement consommable par le codec `json_lines` de Logstash.
