# SENTRA - Logstash Pipeline & MITRE ATT&CK Enrichment

Ce dossier contient la configuration du pipeline d'ingestion Logstash pour la plateforme SOC SENTRA. 
Logstash agit comme le routeur central de données : il reçoit les événements bruts, les normalise, les enrichit avec du contexte MITRE ATT&CK, et les indexe dans Elasticsearch.

## Structure du dossier

*   `pipelines/logstash.conf` : Le fichier de configuration principal (Input, Filter, Output).
*   `dictionaries/mitre-by-sid.yml` : Dictionnaire YAML de correspondance stricte entre un ID de règle Suricata (SID) et une tactique/technique MITRE.
*   `dictionaries/mitre-by-pattern.yml` : Dictionnaire de repli utilisant des expressions régulières sur le nom de l'alerte pour identifier les attaques génériques.
---

## Chaîne de Debug & Traçabilité

Pour valider le bon fonctionnement du pipeline de collecte en cas de dysfonctionnement, suivez la chaîne de validation de bout en bout :

### 1. Flux Cible (Serveur DMZ → SOC)
*   **Étape 1 (Source) :** Vérification de l'agent sur la DMZ (`sudo systemctl status filebeat`).
*   **Étape 2 (Transport) :** Filebeat pousse les logs vers Logstash via TCP sur le port `5044` (`sudo filebeat test output`).
*   **Étape 3 (Ingestion) :** Logstash reçoit, traite et affiche le flux (vérifiable via `docker logs -f logstash`).
*   **Étape 4 (Stockage & UI) :** Indexation dans Elasticsearch (`filebeat-*`) et visualisation dans Kibana (Discover).

### 2. Flux Réseau / IDS (pfSense → SOC)
*   **Étape 1 (Source) :** Suricata intercepte le trafic et écrit les alertes au format brut dans `/var/log/suricata/*/eve.json`.
*   **Étape 2 (Transport) :** `syslog-ng` lit dynamiquement le fichier avec `flags(no-parse)` et l'expédie en flux TCP pur vers Logstash (`192.168.30.10:5000`).
*   **Étape 3 (Ingestion & Enrichissement) :** Logstash applique le filtre MITRE ATT&CK (SID puis Pattern) pour structurer les champs.
*   **Étape 4 (Stockage & UI) :** Indexation dans Elasticsearch (`suricata-*`) et remontée des tactiques/techniques dans le SOC.

---

##  Logique d'Enrichissement MITRE ATT&CK

Le pipeline applique la logique suivante sur les logs `suricata` (format EVE JSON) :
1.  **Recherche par SID (Priorité Haute)** : Mapping déterministe basé sur l'ID de la signature.
2.  **Recherche par Pattern (Regex)** : Si le SID est inconnu, analyse de la chaîne `alert.signature`.
3.  **Fallback** : Assignation à `Unmapped` si aucune règle ne correspond.
4.  **Split** : Création des champs `mitre.tactic`, `mitre.technique_id`, et `mitre.technique_name` prêts pour l'ingestion Elasticsearch.

## Démarrage de l'Ingestion (Mode Isolé)

Le composant Logstash est géré par le `docker-compose.yml` central à la racine du projet. 
Cependant, pour tester le pipeline d'ingestion de manière isolée (sans l'API ML ou le Case Management), vous pouvez utiliser la commande suivante depuis la racine du projet :

```bash
# Démarre uniquement les fondations de données (ELK)
docker compose up -d elasticsearch kibana logstash

# Vérifier que le pipeline est chargé sans erreur de syntaxe
docker logs -f logstash
```
