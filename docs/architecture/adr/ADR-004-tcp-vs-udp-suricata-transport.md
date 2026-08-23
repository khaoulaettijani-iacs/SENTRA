# ADR-004 : Choix du protocole de transport TCP (vs UDP) pour l'acheminement des logs Suricata

Une fois le mode `Filestore` et `syslog-ng` en place sur pfSense pour collecter les logs Suricata, il restait à définir le protocole réseau pour transporter ces flux à travers le réseau virtuel vers la machine SOC (`192.168.30.10:5000`). Traditionnellement, les architectures syslog historiques utilisent le protocole UDP.

Nous avons pris la décision d'utiliser le protocole **TCP** pour acheminer les logs de pfSense vers Logstash, en y associant le template strict `$MSG\n`.

1. **Fiabilité et Garantie de Livraison (Reliability) :** L'UDP est un protocole non orienté connexion. En cas de saturation du réseau ou de pics d'alertes massifs (durant une simulation de DDoS ou de scans agressifs), l'UDP peut perdre des paquets de manière silencieuse. Le TCP garantit un accusé de livraison (handshake, retransmission).
2. **Intégrité du flux JSON :** Le transport TCP, combiné au template `$MSG\n` de syslog-ng, garantit que chaque ligne JSON arrive d'un seul tenant, sans fragmentation réseau susceptible de corrompre le décodage de Logstash.
3. **Séparation des responsabilités :** Le port TCP `5000` est dédié dans le `docker-compose.yml` de Logstash spécifiquement pour recevoir ce flux structuré, garantissant une isolation logique par rapport aux autres flux Beats.

## Conséquences
* **Positif :** Zéro perte de logs d'alertes critiques pendant les tests d'intrusion menés depuis Kali Linux.
* **Négatif :** Légère augmentation de la surcharge réseau (overhead) inhérente au maintien des connexions TCP, négligeable dans le cadre d'un laboratoire virtuel.