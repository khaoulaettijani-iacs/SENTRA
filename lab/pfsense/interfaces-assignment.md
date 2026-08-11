# Assignation des Interfaces pfSense

Ce document décrit la correspondance entre les interfaces physiques/virtuelles VMware, les noms dans pfSense, leurs adresses IP et leur rôle dans l’architecture.

## Table de mapping

# Assignation des Interfaces pfSense

| Nom Physique (pfSense) | Nom Logique | Adresse IP statique | Rôle & Zone |
| :--- | :--- | :--- | :--- |
| `em0` | WAN | DHCP (Client) | Uplink Internet (NAT) |
| `em1` | OPT1 | `192.168.10.1/24` | Passerelle Zone Attaquant (Kali) |
| `em2` | OPT2 | `192.168.20.1/24` | Passerelle Zone DMZ |
| `em3` | LAN | `192.168.30.1/24` | Passerelle Zone SOC |

---

## Détails des sous-réseaux

- **ATTACKER**
  - Subnet : `192.168.10.0/24`
  - Machine : Kali Linux (`192.168.10.10`)
  - Rôle : simulation d’attaques (Nmap, Hydra, scans web)

- **DMZ**
  - Subnet : `192.168.20.0/24`
  - Machine : Ubuntu Server (`192.168.20.10`)
  - Services : Apache2, cible des attaques
  - Logs envoyés vers SOC via Filebeat (port 5044)

- **SOC / LAN**
  - Subnet : `192.168.30.0/24`
  - Machine : Ubuntu SOC (`192.168.30.10`)
  - Rôle : centralisation (ELK, Logstash, ML)

- **WAN**
  - Subnet : `192.168.150.0/24` (NAT VMware)
  - Rôle : accès Internet pour mises à jour, API externes

