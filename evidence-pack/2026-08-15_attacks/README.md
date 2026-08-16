# Scénarios d'Attaques et Preuves

Ce dossier contient les traces d'exécution locales (côté attaquant - Kali Linux) des scénarios d'intrusion générés pour valider le pipeline de détection SENTRA.

## Scénarios Exécutés

| Scénario | Outil Utilisé | Mapping MITRE ATT&CK | 
| :--- | :--- | :--- | :--- |
| **Reconnaissance Réseau** (Stealth, Version, Xmas) | `nmap` | **T1595.001** (Active Scanning: Scanning IP Blocks)<br>**T1046** (Network Service Discovery) |
| **Brute-Force SSH** (Dictionnaire ciblé) | `hydra` | **T1110.001** (Brute Force: Password Guessing) | 
| **Énumération Web** (Vulnérabilités & Répertoires) | `nikto`, `gobuster` | **T1595.003** (Active Scanning: Wordlist Scanning) | 

## Méthodologie
Toutes les attaques ont été lancées depuis la zone isolée `VMnet2` (`192.168.10.10`) vers la DMZ `VMnet3` (`192.168.20.10`). Un horodatage strict (UTC) a été capturé en amont de chaque commande via `date -u` afin de faciliter la corrélation déterministe dans le SIEM (Kibana).