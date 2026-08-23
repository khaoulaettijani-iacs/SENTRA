# SENTRA – Ingestion Layer (ELK, Filebeat & Suricata)

Ce dossier contient la stack d’ingestion centrale de la plateforme SOC SENTRA basée sur Docker Compose, ainsi que la configuration des flux de collecte :
- **Elasticsearch** (stockage et indexation)
- **Kibana** (visualisation et exploration)
- **Logstash** (pipeline d’ingestion et enrichissement MITRE ATT&CK)

---

## Sources de Données & Flux
- **Filebeat** (DMZ, `192.168.20.10`) : Collecte `/var/log/auth.log` et `/var/log/syslog` → Logstash port **5044** (Beats)
- **Suricata** (pfSense, format EVE JSON) : `/var/log/suricata/*/eve.json` → `syslog-ng` → Logstash port **5000** (TCP, JSON lines)

---

## Prérequis & Configuration Kernel 

Elasticsearch nécessite une valeur minimale pour `vm.max_map_count` pour allouer ses index en mémoire.

Configurer sur la machine SOC (Ubuntu, `192.168.30.10`) :
```bash
sudo sysctl -w vm.max_map_count=262144
```
Pour rendre ce paramètre permanent :
```bash
echo "vm.max_map_count=262144" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```
## Démarrage de la Stack
Depuis la machine SOC :
```bash
# Récupérer les derniers fichiers du dépôt
git pull
# Lancer les conteneurs d'ingestion en arrière-plan
docker compose up -d elasticsearch kibana logstash
```

## Ports et Services Déployés

| Service | Port / Protocole | Description / Rôle |
| :--- | :--- | :--- |
| Elasticsearch | 9200 / tcp | API REST, stockage et indexation des logs |
| Kibana | 5601 / tcp | Interface web de visualisation et d'analyse |
| Logstash | 5044 / tcp | Réception des logs système via Filebeat |
| Logstash | 5000 / tcp | Réception des alertes réseau via Suricata / syslog-ng |

Architecture Docker :
- Réseau : soc-net (réseau interne Docker pour la communication inter-services).
- Volumes : esdata (stockage persistant des données Elasticsearch).

## Pipeline Logstash de Référence
```conf
input {
  beats {
    port => 5044
  }
  tcp {
    port  => 5000
    codec => json_lines
    type  => "suricata"
  }
}

filter {
  # Enrichissement MITRE ATT&CK (SID -> Pattern -> Split)
}

output {
  if [type] == "suricata" {
    elasticsearch {
      hosts => ["http://elasticsearch:9200"]
      index => "suricata-%{+YYYY.MM.dd}"
    }
  } else {
    elasticsearch {
      hosts => ["http://elasticsearch:9200"]
      index => "filebeat-%{+YYYY.MM.dd}"
    }
  }
  stdout { codec => rubydebug }  # Mode debug (console)
}
```
## Chaîne de Vérification & Dépannage:
Pour valider le bon fonctionnement de bout en bout, vérifiez dans cet ordre :

1. Filebeat (DMZ) : sudo filebeat test output (doit renvoyer OK)
2. Suricata (pfSense) : tail -f /var/log/suricata/*/eve.json (vérifier l'écriture des flux)
3. Logstash (SOC) : docker logs -f logstash (vérifier la réception des deux flux)
4. Elasticsearch : curl http://localhost:9200/_cat/indices?v (présence des index filebeat-* et suricata-*)
5. Kibana : Ouvrir http://192.168.30.10:5601, configurer les Data Views et consulter l'onglet Discover.

## Pannes Connues & Choix d'Architecture Résolus
- Problème 1 : Le Syslog natif de Suricata tronquait les événements JSON longs (limitation de la norme RFC5424 sur FreeBSD).

* Solution : Utilisation du mode Filestore local couplé à syslog-ng (voir docs/architecture/adr/ADR-003-...).

- Problème 2 : Risque de perte de datagrammes en UDP 5000 lors de pics d'attaques massifs (scans de ports).

* Solution : Passage du transport syslog-ng vers le protocole TCP sur le port 5000 (voir docs/architecture/adr/ADR-004-...).

## Notes de Laboratoire
- xpack.security.enabled=false → Pas d'authentification active (contexte de laboratoire de test).
- discovery.type=single-node → Mode nœud unique Elasticsearch.