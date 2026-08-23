# SENTRA - Logstash Pipeline & MITRE ATT&CK Enrichment

Ce dossier contient la configuration du pipeline d'ingestion Logstash pour la plateforme SOC SENTRA. 
Logstash agit comme le routeur central de données : il reçoit les événements bruts, les normalise, les enrichit avec du contexte MITRE ATT&CK, et les indexe dans Elasticsearch.

## Structure du dossier

*   `pipelines/logstash.conf` : Le fichier de configuration principal (Input, Filter, Output).
*   `dictionaries/mitre-by-sid.yml` : Dictionnaire YAML de correspondance stricte entre un ID de règle Suricata (SID) et une tactique/technique MITRE.
*   `dictionaries/mitre-by-pattern.yml` : Dictionnaire de repli utilisant des expressions régulières sur le nom de l'alerte pour identifier les attaques génériques.

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
