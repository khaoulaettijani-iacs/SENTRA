# Tableau d’adressage – Architecture VMware

## 🔹 Tableau d’adressage

| Réseau VMware                | Interface pfSense | Subnet              | Machine                             |
| ---------------------------- | ----------------- | ------------------- | ----------------------------------- |
| VMnet8 (NAT)                 | WAN (em0)         | Attribué par VMware | pfSense — sortie Internet           |
| VMnet2 (Host-only, DHCP OFF) | OPT1 (em1)        | 192.168.10.0/24     | Kali (192.168.10.10)                |
| VMnet3 (Host-only, DHCP OFF) | OPT2 (em2)        | 192.168.20.0/24     | Ubuntu Server / DMZ (192.168.20.10) |
| VMnet4 (Host-only, DHCP OFF) | OPT3 (em3)        | 192.168.30.0/24     | Ubuntu SOC / SENTRA (192.168.30.10) |

---

## Notes de configuration VMware

### VMnet8

* Type : **NAT**
* DHCP : **Activé**
* Rôle : Accès Internet pour pfSense (WAN)

### VMnet2

* Type : **Host-only**
* DHCP : **Désactivé**
* Subnet : `192.168.10.0/24`
* Rôle : Réseau Attaquant (Kali)

### VMnet3

* Type : **Host-only**
* DHCP : **Désactivé**
* Subnet : `192.168.20.0/24`
* Rôle : Zone DMZ (Ubuntu Server)

### VMnet4

* Type : **Host-only**
* DHCP : **Désactivé**
* Subnet : `192.168.30.0/24`
* Rôle : Réseau SOC / Monitoring (SENTRA)

---

## Remarques

* Toutes les interfaces internes passent par **pfSense (routage + filtrage)**.
* Les communications entre réseaux sont **contrôlées par les règles firewall pfSense**.
* Chaque réseau est isolé pour simuler une architecture réelle :
  * Attaquant (Kali)
  * Cible (DMZ)
  * Centre de supervision (SOC)

---
