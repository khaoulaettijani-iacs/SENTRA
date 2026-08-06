# Ubuntu Server (DMZ) Network & Service Configuration

Ce document décrit la configuration réseau et l’état des services sur le serveur Ubuntu situé dans la DMZ du lab SENTRA.

---

## Configuration réseau

- **Interface réseau VMware** : VMnet3 (Host-Only)
- **Nom interface Ubuntu** : ens33
- **Adresse IP statique** : 192.168.20.10/24
- **Passerelle (Gateway)** : 192.168.20.1 (pfSense - DMZ)
- **DNS** : 8.8.8.8

---

## Configuration appliquée

Configuration réseau statique définie sur le serveur Ubuntu.

Exemple (netplan ou configuration manuelle) :

```bash
sudo ip addr add 192.168.20.10/24 dev eth0
sudo ip route add default via 192.168.20.1
echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf
```
---
## Vérification de la connectivité
- Test vers la passerelle pfSense :
```bash
ping -c 3 192.168.20.1
```
Résultat : Réponses reçues 
Confirme la connectivité entre le serveur DMZ et pfSense

- Test de connectivité depuis Kali :
Ping depuis Kali vers le serveur DMZ
```bash
ping -c 3 192.168.20.10
```
Résultat : Réponses reçues 
Confirme la communication entre réseau Attacker (VMnet2) et DMZ

- Scan réseau (découverte)
```bash
nmap -sn 192.168.20.0/24
```
Résultat : Hôte 192.168.20.10 détecté 
Confirme la visibilité du serveur dans le réseau DMZ
---

## Services actifs
Filebeat :
- Statut : installé et actif 
- Rôle :
Collecte des logs système
Envoi vers Elasticsearch (SOC)
- Vérification :
sudo systemctl status filebeat
- Résultat attendu :
service active (running)
---

- Le serveur DMZ est accessible depuis Kali → environnement prêt pour simulation d’attaques.
- La segmentation réseau fonctionne correctement via pfSense.
- Filebeat est opérationnel

##  Rôle dans l’architecture

Le serveur Ubuntu en DMZ joue le rôle de Machine cible (Victim Server)

Fonctions principales :

- hébergement de services (ex: Apache)
- génération de logs système et sécurité
- point d’observation pour Suricata (trafic réseau)
- source de données pour la pipeline SENTRA

---
