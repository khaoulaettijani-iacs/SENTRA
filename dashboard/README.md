# Visualisation & Dashboard SOC (Kibana)

Ce dossier contient les exports des tableaux de bord Kibana de la plateforme **SENTRA**, permettant la visualisation en temps réel des incidents corrélés et scorés.

## Dashboard : SENTRA — Analyst View

Le tableau de bord `SENTRA — Analyst View` fournit une vue synthétique et décisionnelle dédiée aux analystes SOC (L1/L2) :
- **KPIs d'urgence :** Compteur d'incidents critiques (24h).
- **Répartition volumétrique :** Distribution des niveaux de risque (Critical, High, Medium, Low) et évolution temporelle.
- **Top Menaces :** IP sources récurrentes et techniques MITRE ATT&CK les plus sollicitées.
- **Live Feed :** Flux en direct des événements corrélés (IDS + ML + Risk Score).
- **Filtre dynamique :** Menu déroulant interactif par niveau de risque.

---

## Procédure d'Importation (Reproductibilité)

Si vous déployez la plateforme SENTRA sur un nouvel environnement ELK, vous pouvez restaurer l'intégralité du tableau de bord et de ses visualisations sans configuration manuelle :

1. Accédez à l'interface web de Kibana (`http://<SOC_VM_IP>:5601`).
2. Naviguez vers **Management** > **Stack Management** > **Saved Objects**.
3. Cliquez sur le bouton **Import** en haut à droite.
4. Sélectionnez le fichier :
   `dashboard/kibana-exports/sentra-analyst-dashboard.ndjson`
5. Si un conflit de Data View apparaît, associez le fichier au Data View `correlated-events`.
6. Rendez-vous dans **Analytics** > **Dashboards** pour ouvrir `SENTRA — Analyst View`.