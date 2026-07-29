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

