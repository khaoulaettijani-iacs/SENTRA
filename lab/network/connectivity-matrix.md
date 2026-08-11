# Matrice de Validation de la Connectivité et Segmentation (Firewall)

Ce document prouve l'efficacité de la segmentation réseau appliquée sur pfSense. Les flux non autorisés sont bloqués "by design" afin de contenir les compromissions.

| Source | Destination | Méthode de Test | Attendu | Résultat Confirmé | Commentaire |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Kali (10.10)** | pfSense OPT1 (10.1) | `ping` | Autorisé |  Pass | Test de la passerelle attaquant |
| **Kali (10.10)** | DMZ (20.10) | `nmap -sn` / `ping` | Autorisé |  Pass | Vecteur d'attaque principal |
| **Kali (10.10)** | SOC (30.10) | `ping` | **Bloqué** |  Bloqué | L'attaquant ne doit pas atteindre l'infra de sécu |
| **Kali (10.10)** | Internet (8.8.8.8) | `ping` | Autorisé |  Pass | Accès requis pour les outils externes |
| **DMZ (20.10)** | SOC (30.10) : TCP 5044 | `telnet` / `nc` | Autorisé |  Pass | Requis pour Filebeat -> Logstash |
| **DMZ (20.10)** | Kali (10.10) | `ping` | **Bloqué** |  Bloqué | La DMZ n'initie pas de flux vers l'attaquant |
| **DMZ (20.10)** | Internet | `ping` | Autorisé |  Pass | Requis pour `apt update` |
| **SOC (30.10)** | Internet | `ping` | Autorisé |  Pass | Requis pour `docker pull` et API OSINT |
| **SOC (30.10)** | Kali (10.10) | `ping` | **Bloqué** |  Bloqué | Isolation du Management |