# Modèle de Rapport d'Incident SOC (SENTRA)

Ce document décrit la structure standardisée des rapports générés automatiquement par le module `reporting-engine` de la plateforme SENTRA. 

## Structure du Livrable (PDF / TXT)

=================================================================
RAPPORT D'INCIDENT DE SÉCURITÉ — SENTRA
=================================================================
Généré le : [Date et Heure UTC]
Référence  : [ID Unique UUIDv4 tronqué]

RÉSUMÉ EXÉCUTIF
-----------------------------------------------------------------
Le [Horodatage de l'événement], une activité classée [Niveau de Risque] (score [Score]/100)
a été détectée depuis [IP Source] vers [IP Destination].
L'alerte "[Signature de l'alerte]" a été associée à la technique MITRE ATT&CK
[ID Technique] ([Nom de la Technique]), tactique [Tactique].

DÉTAILS TECHNIQUES
-----------------------------------------------------------------
Horodatage              : [Timestamp Elasticsearch]
IP source                : [Adresse IP]
IP destination            : [Adresse IP]
Signature IDS             : [Nom de la règle Suricata]
Sévérité IDS (Suricata)   : [1, 2, 3 ou -]
Tactique MITRE             : [Ex: Credential Access, Reconnaissance...]
Technique MITRE            : [ID] — [Nom]
Probabilité Random Forest : [0.000 à 1.000]
Score Isolation Forest    : [Score brut d'anomalie]
Score de risque final     : [0-100] ([Low/Medium/High/Critical])

DÉCOMPOSITION DU SCORE
-----------------------------------------------------------------
Composante IDS    : [Points] / 35
Composante MITRE  : [Points] / 15
Composante RF      : [Points] / 30
Composante IF      : [Points] / 20

RECOMMANDATIONS
-----------------------------------------------------------------
- [Action de remédiation 1 dictée par le playbook (selon MITRE et Risque)]
- [Action de remédiation 2]
- [Action de remédiation 3]

-----------------------------------------------------------------
Rapport généré automatiquement par le moteur de reporting SENTRA.
=================================================================