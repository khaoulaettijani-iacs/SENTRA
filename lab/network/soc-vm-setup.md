# Ubuntu SOC / SENTRA VM — Network & Docker Setup

Ce document décrit la configuration réseau et l’installation de Docker sur la machine SOC (SENTRA), responsable de la centralisation et de l’analyse des logs.

---

## Configuration réseau

- **Interface réseau VMware** : VMnet4 (Host-Only)
- **Nom interface Ubuntu** : ens33
- **Adresse IP statique** : 192.168.30.10/24
- **Passerelle (Gateway)** : 192.168.30.1 (pfSense - SOC / LAN)
- **DNS** : 8.8.8.8

---

## Configuration appliquée

Configuration réseau statique :

```bash
sudo ip addr add 192.168.30.10/24 dev eth0
sudo ip route add default via 192.168.30.1
echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf
```
---

## Vérification de la connectivité (local)
- Test vers la passerelle pfSense :
```bash
ping -c 3 192.168.30.1
```
Résultat : Réponses reçues 
Connectivité avec pfSense confirmée

- Test de connectivité depuis la DMZ : 
Ping depuis Ubuntu Server (DMZ)
```bash
ping -c 3 192.168.30.10
```
Résultat : Réponses reçues 
Confirme la communication entre la DMZ et le SOC

- Installation de Docker :
Docker est installé et fonctionnel sur la machine SOC.
Vérification version :
```bash
docker --version
```
Exemple de résultat :
Docker version 24.x.x, build xxxx

Test de fonctionnement :
```bash
docker run hello-world
```
Résultat :
Message de confirmation affiché 
Docker fonctionne correctement

---

- La connectivité réseau entre les segments DMZ et SOC est fonctionnelle.
- Docker est correctement installé → prêt pour déploiement ELK (Elasticsearch, Logstash, Kibana)
- La machine SOC peut recevoir les logs depuis la DMZ (Filebeat), analyser les événements et héberger les composants SENTRA.
---

## Rôle dans l’architecture

La machine Ubuntu SOC joue le rôle de Centre d’Analyse (SOC / SIEM - SENTRA)

Fonctions principales :
- Centralisation des logs (Filebeat → Elasticsearch)
- Analyse et visualisation (Kibana)
- Détection d’intrusions (corrélation + ML)
- Enrichissement via Threat Intelligence

