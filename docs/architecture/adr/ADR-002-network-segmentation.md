# ADR 002 : Zero-Trust et Segmentation Réseau du Laboratoire

Pour tester la plateforme SOC SENTRA, une machine attaquante (Kali Linux) doit générer du trafic malveillant vers une cible (Ubuntu DMZ). Il est impératif d'isoler l'infrastructure de sécurité (SOC) pour éviter sa compromission pendant les tests.

L'architecture repose sur une topologie de **Segmentation stricte via pfSense** (Micro-segmentation). La machine Kali a accès à Internet (WAN) et à la DMZ, mais n'a aucun chemin de routage vers le réseau de management (SOC).

Cela se justifie par :
1.  **Réalisme architectural :** Dans une entreprise, le réseau de management d'un SIEM n'est jamais exposé aux utilisateurs ou aux réseaux non de confiance. 
2.  **Principe du moindre privilège (Zero-Trust) :** Le pare-feu pfSense bloque le trafic par défaut. Seules les communications explicitement nécessaires sont autorisées (ex: TCP 5044 de la DMZ vers Logstash).
3.  **Accès Internet pour Kali (NAT) :** Autoriser Kali à joindre Internet permet de simuler le téléchargement de payloads ou la mise à jour d'outils d'attaque (`apt update`, scripts GitHub) sans exposer le réseau hôte (Windows).

## Conséquences
*   **Positif :** L'environnement de test est confiné et sécurisé. Une compromission totale de la machine cible (DMZ) ne permet pas de rebondir (Pivoting) vers la machine SOC.
*   **Négatif :** Ajoute une complexité de gestion du routage. La configuration de VMware doit être strictement contrôlée (désactivation du DHCP local pour les VMnets) pour forcer pfSense à agir comme unique passerelle.