# SOC Platform - Threat Detection Project

## Objective
Build a SOC platform to detect attacks using IDS, ML and ELK Stack.

## Architecture
- Attacker: Kali Linux
- Firewall: pfSense
- Target: Ubuntu Server (DMZ)
- SOC: Ubuntu + ELK (Docker)

## Networks
- Attacker: 192.168.10.0/24
- DMZ: 192.168.20.0/24
- SOC: 192.168.30.0/24
- WAN: NAT

## Stack
- Elasticsearch
- Logstash
- Kibana
- Docker Compose

## Repository

```text
SENTRA/
├── README.md                          # overview, badges, quickstart
├── LICENSE
├── docker-compose.yml                 # ELK + backend + postgres
├── .env.example
├── setup.sh                           # script de setup reproductible 
│
├── docs/
│   ├── architecture/
│   │   ├── architecture-diagram.png       # export du diagramme global
│   │   ├── network-diagram.png            # export topologie pfSense/VMnets
│   │   ├── attack-scenario-flow.png        # export scénario d'attaque
│   │   ├── data-flow-diagram.png
│   │   └── adr/
│   │       ├── ADR-001-elk-vs-splunk.md
│   │       ├── ADR-002-suricata-vs-snort.md
│   │       ├── ADR-003-rf-plus-isolation-forest.md
│   │       └── ADR-004-postgresql-persistence.md
│   ├── risk-scoring-methodology.md
│   ├── incident-report-template.md
│   ├── validation-checklist.md
│   ├── risk-register.md
│   └── executive-summary.md
│
├── lab/
│   ├── pfsense/                        # config, règles NAT/firewall
│   ├── network/                        # tableau d'adressage, schémas VMnet
│   └── vagrant/                        
│
├── ingestion/
│   ├── filebeat/filebeat.yml
│   ├── logstash/pipelines/
│   └── suricata/
│       ├── suricata.yaml
│       └── rules/custom.rules
│
├── ml/
│   ├── notebooks/01_preprocessing.ipynb
│   ├── notebooks/02_random_forest.ipynb
│   ├── notebooks/03_isolation_forest.ipynb
│   ├── data/README.md                  
│   ├── models/                         # .pkl versionnés 
│   └── train.py
│
├── correlation-engine/                 # service Python
├── risk-scoring-engine/                # service Python
├── backend-api/                        # API interne 
│
├── dashboard/                          # frontend léger ou config Kibana
├── reporting/
│   └── templates/incident_report.j2
│
├── database/
│   └── postgresql/
│       ├── schema.sql
│       └── migrations/
│
├── enrichment/                         # GeoIP, AbuseIPDB, VirusTotal/MISP
├── notifications/                      # email + webhook
│
├── evidence-pack/
│   └── 2026-08-XX_scenario-nmap/       
│       ├── screenshots/
│       └── logs/
│
├── tests/
└── scripts/                            # scripts de rejeu des scénarios d'attaque
```