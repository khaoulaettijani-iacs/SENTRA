# SENTRA — Moteur de Reporting Automatisé (NLG)

## Rôle du composant
Le module de reporting est un microservice chargé de générer des rapports d'incidents de sécurité (Security Incident Reports) automatisés. Il interroge la base de données Elasticsearch pour récupérer les événements corrélés, les enrichit avec des recommandations d'atténuation (Mitigation), et génère des livrables exportables (PDF et TXT).

## Choix Techniques
- **Framework Web :** FastAPI (pour des performances optimales et une documentation Swagger native).
- **Templating :** Jinja2 (séparation stricte de la logique et de la présentation).
- **Génération PDF :** ReportLab. Ce choix d'ingénierie permet de générer des PDF nativement en Python sans dépendre d'outils système lourds (comme `wkhtmltopdf` ou un navigateur headless), garantissant un conteneur Docker minimaliste et sécurisé.
- **Base de données :** Client Elasticsearch (épinglé en v8.12.0 pour correspondre à l'infrastructure SOC).

## API Endpoints
Le service écoute sur le port `8003`.

- `POST /report/{event_id}` : Déclenche la génération d'un rapport pour un événement spécifique. Retourne un identifiant d'incident court (`incident_id`).
- `GET /report/{incident_id}/pdf` : Télécharge le rapport au format PDF.
- `GET /report/{incident_id}/txt` : Télécharge le rapport au format texte brut.

## Utilisation

```bash
# Générer un rapport à partir d'un Event ID Elasticsearch
curl -X POST http://localhost:8003/report/<event_id>

# Récupérer le fichier PDF généré
curl http://localhost:8003/report/<incident_id>/pdf -o incident_report.pdf