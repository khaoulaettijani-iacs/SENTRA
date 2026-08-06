# Kali Linux Network Configuration (VMnet2)

Ce document décrit la configuration réseau appliquée à la machine Kali Linux dans le lab SENTRA, ainsi que les tests de connectivité réalisés.

---

## Configuration réseau

- **Interface réseau VMware** : VMnet2 (Host-Only)
- **Nom interface Kali** : eth0
- **Adresse IP statique** : 192.168.10.10/24
- **Passerelle (Gateway)** : 192.168.10.1 (pfSense - ATTACKER)
- **DNS** : 8.8.8.8

---

## Configuration appliquée

Configuration effectuée manuellement avec une IP statique :

```bash
sudo ip addr add 192.168.10.10/24 dev eth0
sudo ip route add default via 192.168.10.1
echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf
```

---

## Vérification de la configuration

Commande utilisée :

```bash
ip a
```

Résultat :

Interface eth0 correctement assignée avec l’adresse 192.168.10.10/24

---

##  Tests de connectivité
1. Test vers la passerelle (pfSense)
```bash
ping -c 3 192.168.10.1
```

Résultat :
Réponses reçues 
Latence faible (réseau local)

2. Test vers Internet (Google DNS)
```bash
ping -c 3 8.8.8.8
```
Résultat :
Réponses reçues 
Confirme que le NAT pfSense fonctionne correctement


Les captures suivantes sont disponibles :
- ip a (configuration IP)
- ping 192.168.10.1 (connectivité locale)

 Chemin : lab/network/screenshots/kali-network-test.png


La communication entre Kali et pfSense est fonctionnelle.
L’accès Internet est opérationnel via le NAT (WAN).
La machine Kali est prête pour les phases d’attaque :
Scan réseau (Nmap)
Brute force (Hydra)
Tests web (Nikto / ZAP)

---

## Rôle dans l’architecture

Kali Linux joue le rôle de Machine attaquante (Attacker Node). 
Elle est utilisée pour générer du trafic malveillant afin de :
- tester la détection par Suricata
- générer des logs (Filebeat → ELK)
- alimenter le moteur de corrélation SENTRA

---
