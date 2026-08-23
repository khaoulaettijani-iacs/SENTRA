# Configuration des Réseaux Virtuels (VMware)

## Tableau d’adressage

| Interface pfSense | Subnet | Rôle Machine | VMnet VMware | Type VMware | DHCP VMware |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **WAN** (em0) | Attribué par VMware | pfSense — Sortie Internet | **VMnet8** | NAT | Activé |
| **OPT1** (em1) | `192.168.10.0/24` | Kali Linux (192.168.10.10) | **VMnet2** | Host-only | Désactivé |
| **OPT2** (em2) | `192.168.20.0/24` | Ubuntu DMZ (192.168.20.10) | **VMnet3** | Host-only | Désactivé |
| **OPT3** (em3) | `192.168.30.0/24` | Ubuntu SOC (192.168.30.10) | **VMnet4** | Host-only | Désactivé |

