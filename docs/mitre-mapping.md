# Mapping MITRE ATT&CK - Scénarios de Détection SENTRA

Ce document établit la correspondance formelle entre les attaques simulées dans le laboratoire, les signatures de détection (Suricata ET Open & Custom) et le framework MITRE ATT&CK. Ce mapping permet aux analystes d'identifier rapidement la tactique et la technique employées par une menace.

| Scénario d'Attaque | Commande Utilisée (Kali) | Signature Suricata Déclenchée | Tactique MITRE | Technique MITRE |
| :--- | :--- | :--- | :--- | :--- |
| **Découverte d'hôtes** | `nmap -sn` | `ET SCAN Nmap` | Reconnaissance (TA0043) | **T1595.001** (Active Scanning: Scanning IP Blocks) |
| **Scan de ports (SYN/Version/Scripts/Xmas)** | `nmap -sS`, `-sV -A`, `-sX` | `ET SCAN Nmap Scripting Engine` / `SENTRA CUSTOM Suspicious TCP Scan Flags` | Reconnaissance (TA0043) | **T1595.002** (Active Scanning: Vulnerability Scanning) |
| **Brute-force SSH** | `hydra ssh://` | `SENTRA CUSTOM SSH Brute Force Attempt` | Credential Access (TA0006) | **T1110.001** (Brute Force: Password Guessing) |
| **Scan de vulnérabilités Web** | `nikto` | `ET SCAN` / `ET WEB_SERVER` | Reconnaissance (TA0043) | **T1595.002** (Active Scanning: Vulnerability Scanning) |
| **Énumération de répertoires Web** | `gobuster dir` | `SENTRA CUSTOM Web Directory Bruteforce Attempt` | Reconnaissance (TA0043) | **T1595.003** (Active Scanning: Wordlist Scanning) |

## Analyse de Couverture
Le prototype actuel démontre une capacité de détection transverse couvrant de multiples vecteurs. Avec seulement trois scénarios de tests majeurs (Nmap, SSH, Web), l'IDS Suricata couplé à la centralisation ELK parvient à identifier des comportements malveillants s'étalant sur **deux tactiques distinctes** du framework ATT&CK (Reconnaissance et Credential Access) et **trois sous-techniques** de scan actif.