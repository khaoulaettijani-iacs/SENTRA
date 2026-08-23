# Configuration de l'Agent Filebeat (DMZ)

Ce dossier contient la configuration de l'agent **Filebeat**, déployé sur le serveur Ubuntu de la DMZ (`192.168.20.10`), chargé de collecter et d'expédier les journaux système et d'authentification vers le pipeline Logstash du SOC.

## Fichiers du dossier
*   `filebeat.yml` : Fichier de configuration principal de l'agent.

---

##  Déploiement et Configuration sur la DMZ

1. **Installation de Filebeat (si ce n'est pas déjà fait) :**
   ```bash
   curl -L -O [https://artifacts.elastic.co/downloads/beats/filebeat/filebeat-8.12.0-amd64.deb](https://artifacts.elastic.co/downloads/beats/filebeat/filebeat-8.12.0-amd64.deb)
   sudo dpkg -i filebeat-8.12.0-amd64.deb
   ```
2. **Mise en place du fichier de configuration :**

Copier le contenu de filebeat.yml dans le fichier de configuration officiel du système:
```bash
sudo cp filebeat.yml /etc/filebeat/filebeat.yml
sudo chmod 644 /etc/filebeat/filebeat.yml
```
3. Activation et démarrage du service :
```bash
sudo systemctl enable filebeat
sudo systemctl restart filebeat
```
## Validation et Tests

Avant de valider le flux, Filebeat propose des commandes intégrées pour tester la syntaxe et la connectivité réseau :

1. Valider la syntaxe du fichier de configuration
```bash
sudo filebeat test config
```
(Résultat attendu : Config file successfully validated)

2. Valider la connectivité réseau vers Logstash (SOC)
```bash
sudo filebeat test output
```
(Résultat attendu : Connexion établie vers 192.168.30.10:5044 avec un statut OK)

## Dépannage (Troubleshooting)

1. Vérifier l'état du service :
```bash
sudo systemctl status filebeat
```
2. Consulter les logs internes de Filebeat en cas d'erreur de transport :
```bash
sudo tail -f /var/log/filebeat/filebeat.log
```
3. Vérifier les règles de pare-feu pfSense :
Si test output échoue, assurez-vous que la règle autorisant le trafic TCP de la DMZ vers le SOC sur le port 5044 est bien active sur l'interface OPT2 de pfSense.

---
