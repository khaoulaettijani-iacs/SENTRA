# Mapping MITRE ATT&CK - Scénarios de Détection SENTRA

Ce document établit la correspondance formelle entre les attaques simulées dans le laboratoire, les signatures de détection (Suricata ET Open & Custom) et le framework MITRE ATT&CK. Ce mapping permet aux analystes d'identifier rapidement la tactique et la technique employées par une menace.

## Stratégie de Classification

L'architecture SENTRA utilise une approche hybride pour garantir une couverture maximale :
1. **Règles Custom (SENTRA) :** Mappées par ID de signature exact (SID).
2. **Règles Communautaires (ET Open) :** Mappées par extraction de motifs (Regex) sur le libellé de l'alerte.

| Scénario d'Attaque | Commande Utilisée (Kali) | Signature Suricata Déclenchée | Tactique MITRE | Technique MITRE |
| :--- | :--- | :--- | :--- | :--- |
| **Découverte d'hôtes** | `nmap -sn` | `ET SCAN Nmap` | Reconnaissance (TA0043) | **T1595.001** (Active Scanning: Scanning IP Blocks) |
| **Scan de ports (SYN/Version/Scripts/Xmas)** | `nmap -sS`, `-sV -A`, `-sX` | `ET SCAN Nmap Scripting Engine` / `SENTRA CUSTOM Suspicious TCP Scan Flags` | Reconnaissance (TA0043) | **T1595.002** (Active Scanning: Vulnerability Scanning) |
| **Brute-force SSH** | `hydra ssh://` | `SENTRA CUSTOM SSH Brute Force Attempt` | Credential Access (TA0006) | **T1110.001** (Brute Force: Password Guessing) |
| **Scan de vulnérabilités Web** | `nikto` | `ET SCAN` / `ET WEB_SERVER` | Reconnaissance (TA0043) | **T1595.002** (Active Scanning: Vulnerability Scanning) |
| **Énumération de répertoires Web** | `gobuster dir` | `SENTRA CUSTOM Web Directory Bruteforce Attempt` | Reconnaissance (TA0043) | **T1595.003** (Active Scanning: Wordlist Scanning) |

## Mappings Actifs 

| Détection / Signature (Regex ou SID) | MITRE Tactic | MITRE Technique ID | MITRE Technique Name |
| :--- | :--- | :--- | :--- |
| `9000001` (Xmas Scan) | Reconnaissance | T1595.002 | Active Scanning: Vulnerability Scanning |
| `9000002` (SSH Brute Force) | Credential Access | T1110.001 | Brute Force: Password Guessing |
| `9000003` (Web Dir Enum) | Reconnaissance | T1595.003 | Active Scanning: Wordlist Scanning |
| `(?i)nmap` (ET Open) | Reconnaissance | T1595.002 | Active Scanning: Vulnerability Scanning |
| `(?i)ssh.*(scan|brute)` | Credential Access | T1110.001 | Brute Force: Password Guessing |

Pour modifier ces correspondances ou en ajouter de nouvelles, veuillez éditer les fichiers YAML correspondants. Logstash rechargera automatiquement la configuration toutes les 5 minutes.