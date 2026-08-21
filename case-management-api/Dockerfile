# Utilisation d'une image Python légère
FROM python:3.11-slim

# Définition du répertoire de travail dans le conteneur
WORKDIR /app

# Copie du fichier des dépendances
COPY requirements.txt .

# Installation des dépendances sans utiliser le cache pour alléger l'image
RUN pip install --no-cache-dir -r requirements.txt

# Copie de tout le code source de l'API dans le conteneur
COPY . .

# Lancement de l'API FastAPI via le serveur Uvicorn sur le port 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]