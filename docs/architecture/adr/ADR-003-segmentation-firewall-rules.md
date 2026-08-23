# ADR-001 — Segmentation réseau et règles firewall pfSense

##  Contexte

Dans le cadre du projet SENTRA, un environnement de laboratoire sécurisé a été conçu afin de simuler une architecture SOC réaliste.  

L’objectif est de :
- isoler les différents segments réseau (Attacker, DMZ, SOC)
- contrôler les flux entre ces segments
- permettre uniquement les communications nécessaires au fonctionnement du pipeline de détection

Le pare-feu pfSense est utilisé comme point central de filtrage et de routage.

---

##  Architecture réseau

Trois zones principales sont définies :

| Zone | Réseau | Rôle |
|------|--------|------|
| OPT1 | 192.168.10.0/24 | Attacker (Kali Linux) |
| OPT2 | 192.168.20.0/24 | DMZ (Ubuntu Server) |
| OPT3 | 192.168.30.0/24 | SOC / SENTRA |

---

##  Décision

Une stratégie de **segmentation stricte avec principe de moindre privilège** a été adoptée :

- Blocage par défaut des flux non nécessaires
- Autorisation explicite uniquement des communications utiles
- Isolation forte du SOC (zone critique)

---

##  Règles Firewall

### WAN

- Activation des protections par défaut :
  - Block bogon networks
  - Block private networks

Objectif :
- empêcher les connexions invalides ou spoofées depuis Internet

---

###  ATTACKER (Kali)

| # | Action | Source | Destination | Protocole | Port | Justification |
|---|---|---|---|---|---|---|
| 1 | Block | OPT1 net | 192.168.30.0/24 (SOC) | any | any | Empêcher tout accès direct au SOC |
| 2 | Pass | OPT1 net | 192.168.20.0/24 (DMZ) | any | any | Permettre les scénarios d’attaque |
| 3 | Pass | OPT1 net | any | any | any | Accès Internet |

 Choix :
- Kali est considéré comme **non fiable**
- Il peut attaquer la DMZ mais jamais accéder au SOC

---

### DMZ (Ubuntu Server)

| # | Action | Source | Destination | Protocole | Port | Justification |
|---|---|---|---|---|---|---|
| 1 | Pass | OPT2 net | 192.168.30.10 (SOC) | TCP | 5044 | Envoi des logs via Filebeat |
| 2 | Block | OPT2 net | 192.168.10.0/24 (Kali) | any | any | Interdire toute initiative vers l’attaquant |
| 3 | Pass | OPT2 net | any | any | any | Accès Internet (mises à jour) |

Choix :
- La DMZ est semi-exposée
- Elle peut envoyer des logs mais ne doit pas initier vers Kali

---

### SOC (SENTRA)

| # | Action | Source | Destination | Protocole | Port | Justification |
|---|---|---|---|---|---|---|
| 1 | Block | OPT3 net | 192.168.10.0/24 (Kali) | any | any | Protection du SOC |
| 2 | Pass | OPT3 net | any | any | any | Accès Internet (Docker, API TI) |

Choix :
- Le SOC est une **zone critique**
- Aucun flux vers l’attaquant n’est autorisé

---

## Conséquences

- Isolation forte des zones critiques (SOC)
- Réduction de la surface d’attaque
- Simulation réaliste d’une architecture entreprise
- Contrôle précis des flux réseau

---

## Limites

- Kali a accès à Internet (moins réaliste en environnement sécurisé) pour la mise à jour des outils offensifs
- Les règles sont permissives pour simplifier le lab
- Pas encore de filtrage fin (ports spécifiques hors Filebeat)

---

## Améliorations possibles

- Bloquer Internet pour Kali (egress filtering)
- Restreindre DMZ → Internet (ports 80/443 uniquement)
- Ajouter IDS/IPS inline (Suricata IPS mode)
- Implémenter des règles basées sur les ports/services
- Ajouter une zone interne supplémentaire (ex: réseau utilisateur)

---

## Conclusion

La stratégie de segmentation adoptée permet de :

- protéger efficacement le SOC
- simuler des attaques réalistes sur la DMZ
- assurer le bon fonctionnement du pipeline SENTRA (collecte + analyse)

Cette décision constitue une base solide pour les étapes suivantes :
détection, corrélation et analyse des incidents.
