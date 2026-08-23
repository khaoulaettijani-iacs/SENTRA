# ADR-004 : Stratégie d'Enrichissement Dynamique MITRE ATT&CK


## Contexte
Le SOC SENTRA génère des alertes de sécurité (via Suricata) qui nécessitent une contextualisation immédiate pour faciliter l'analyse L1 et préparer les futures phases de Machine Learning. Il est nécessaire de mapper ces alertes brutes vers le framework MITRE ATT&CK (Tactiques et Techniques) au vol, avant l'indexation dans Elasticsearch.

## Décision
Nous avons opté pour une approche à deux niveaux intégrée directement dans le pipeline Logstash via le filtre `translate`, utilisant deux dictionnaires YAML distincts :

1. **Priorité 1 : Mapping exact par SID (`mitre-by-sid.yml`)**
   - **Justification :** Nos règles personnalisées (SENTRA CUSTOM) possèdent des identifiants (SID) connus et fixes. Le matching exact garantit une précision de 100% sur nos scénarios d'attaque spécifiques avec un coût de calcul minimal.

2. **Priorité 2 : Mapping par expression régulière (`mitre-by-pattern.yml`)**
   - **Justification :** Le ruleset ET Open génère des alertes dont les SID peuvent changer ou ne pas être connus à l'avance. L'utilisation de Regex sur le champ `alert.signature` sert de filet de sécurité robuste pour catégoriser ces alertes imprévues.

3. **Gestion des exceptions : Tagging Explicite (`Unmapped`)**
   - **Justification :** Toute alerte ne correspondant à aucun dictionnaire est explicitement taguée `Unmapped` avec une valeur de repli (`fallback`). Cela garantit la traçabilité et l'auditabilité : plutôt que d'ignorer silencieusement les nouvelles alertes, ce tag indique à l'équipe SOC qu'un nouveau pattern doit être ajouté aux dictionnaires, favorisant l'amélioration continue.

## Conséquences
- **Avantages :** Enrichissement temps réel, découplage de la configuration (les dictionnaires sont mis à jour sans redémarrer Logstash grâce à `refresh_interval`), création de *features* catégorielles propres pour les futurs modèles de Machine Learning.
- **Inconvénients :** Nécessite une maintenance régulière du fichier `mitre-by-pattern.yml` pour réduire les alertes `Unmapped`.