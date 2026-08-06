# Connectivity Matrix — SENTRA Lab

Cette matrice valide la segmentation réseau et les règles de communication entre les différentes zones du lab.

---

## Méthodologie

Chaque flux est testé avec :
- `ping` → connectivité réseau
- `nmap` → visibilité des hôtes

---

## 📊 Matrice de connectivité

| Depuis | Vers | Attendu | Testé (ping/nmap) | Résultat | Commentaire |
|--------|------|---------|-------------------|----------|-------------|
| Kali (192.168.10.10) | pfSense OPT1 (192.168.10.1) | reachable | ping OK |  SUCCESS | Gateway accessible |
| Kali (192.168.10.10) | DMZ (192.168.20.10) | reachable | ping OK, nmap OK |  SUCCESS | Accès autorisé pour simulation d’attaque |
| Kali (192.168.10.10) | SOC (192.168.30.10) | blocked | ping FAIL |  BLOCKED | Isolation du SOC (sécurité) |
| Kali (192.168.10.10) | Internet (8.8.8.8) | blocked | ping OK |  PARTIAL | accès Internet autorisé |
| DMZ (192.168.20.10) | SOC (192.168.30.10) | reachable | ping OK | SUCCESS | Transmission logs (Filebeat) |
| DMZ (192.168.20.10) | Internet | reachable | ping OK | SUCCESS | Accès nécessaire pour updates |
| SOC (192.168.30.10) | Internet | reachable | ping OK | SUCCESS | Docker pull / mises à jour |

---

## Analyse

- La segmentation réseau est globalement respectée
- Le SOC est correctement isolé des accès directs depuis Kali
- La communication DMZ → SOC est fonctionnelle (pipeline logs)
- L’accès Internet est actif via NAT pfSense

---

## Conclusion

La matrice confirme que l’architecture SENTRA :

- respecte les principes de segmentation réseau
- isole les composants critiques (SOC)
- permet les flux nécessaires au fonctionnement (logs, monitoring)
