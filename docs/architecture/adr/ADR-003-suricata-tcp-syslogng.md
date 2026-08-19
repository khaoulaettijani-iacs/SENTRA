# ADR-003 : Contournement de la limitation Syslog UDP via syslog-ng et TCP pour Suricata

## Statut
Accepté et Validé en intégration.

## Contexte
L'ingestion initiale des alertes Suricata (format EVE JSON) reposait sur le module Syslog natif de pfSense envoyant des datagrammes UDP sur le port 5000. Lors des tests de charge (scans Nmap), une perte totale des alertes a été constatée dans Kibana. L'investigation a démontré que la longueur des payloads JSON générés par Suricata dépassait la taille maximale autorisée par le syslog FreeBSD (RFC5424), entraînant une corruption de la structure JSON en transit et un rejet par le pipeline Logstash.

## Décision
Pour fiabiliser le pipeline de données (prérequis strict pour le futur moteur de corrélation ML) :
1. **Désactivation de l'export syslog natif** dans Suricata au profit d'une écriture locale (`Filestore`).
2. **Déploiement du paquet `syslog-ng`** sur le pare-feu pour monitorer le fichier `eve.json`.
3. **Changement de protocole (UDP vers TCP)** pour expédier les logs vers Logstash.
4. **Application du template `$MSG\n`** pour transmettre un flux JSON pur, éliminant le besoin d'un filtre `grok` complexe côté SOC.
