# SENTRA – Ingestion Layer (ELK + Logstash)

Ce dossier contient la stack d’ingestion du projet SENTRA basée sur Docker Compose :
- Elasticsearch (stockage)
- Kibana (visualisation)
- Logstash (pipeline d’ingestion)

---

## VM SOC prête
- Ubuntu SOC configuré (VMnet4 – 192.168.30.10)
- Accès réseau OK (gateway 192.168.30.1)
- Docker installé et fonctionnel

Vérification :
```bash
docker --version
docker run hello-world
```

## Configuration kernel (IMPORTANT)

Elasticsearch nécessite une valeur minimale pour vm.max_map_count.

Configurer sur la VM SOC :
```bash
sudo sysctl -w vm.max_map_count=262144
```

Pour rendre permanent :
```bash
echo "vm.max_map_count=262144" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```
## Lancement de la stack

Depuis la VM SOC :
```bash
# récupérer les derniers fichiers
git pull
# lancer les conteneurs
docker compose up -d
```

## Services déployés
Elasticsearch :

URL: http://localhost:9200
Rôle : stockage et indexation des logs

Kibana :
URL : http://localhost:5601
Rôle : visualisation et analyse

Logstash :
Port Beats : 5044 (Filebeat → Logstash)
Port UDP : 5000 (Suricata via pfSense)

## Ports utilisés
```text
| Service       | Port     | Description     |
| ------------- | -------- | --------------- |
| Elasticsearch | 9200     | API REST        |
| Kibana        | 5601     | Interface web   |
| Logstash      | 5044     | Entrée Filebeat |
| Logstash      | 5000/udp | Entrée Suricata |
```

## Architecture Docker
Réseau
soc-net : réseau interne Docker pour communication entre services
Volume
esdata : stockage persistant Elasticsearch

## Pipeline Logstash
```bash
input {
  beats {
    port => 5044
  }
  udp {
    port  => 5000
    codec => json
    type  => "suricata"
  }
}
filter {
  # Phase 3 :
  # - Parsing logs
  # - Enrichissement GeoIP
  # - Mapping MITRE ATT&CK
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

  stdout { codec => rubydebug }  # debug (à désactiver en production)
}
```
## Notes importantes
xpack.security.enabled=false → pas d’authentification (lab uniquement)
discovery.type=single-node → mode standalone
mémoire Java limitée à 512MB (adapter selon RAM)

## Vérification
```bash
docker ps
```
Attendu :
elasticsearch → healthy
kibana → running
logstash → running

Test Elasticsearch :
```bash
curl http://localhost:9200
```

Accès Kibana :
ouvrir navigateur → http://192.168.30.10:5601

## Objectif

Cette stack permet :

ingestion des logs système (Filebeat)
ingestion des alertes réseau (Suricata)
centralisation dans Elasticsearch
visualisation via Kibana

## tapes suivantes
Installer Filebeat sur DMZ
Connecter Filebeat → Logstash
Configurer Suricata → Logstash (UDP 5000)
Créer index patterns dans Kibana
Valider pipeline end-to-end
