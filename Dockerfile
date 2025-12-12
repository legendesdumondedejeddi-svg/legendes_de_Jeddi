# Image Python officielle, légère, propre
FROM python:3.13-slim

# Empêche Python de bufferiser (meilleure compatibilité logs Render)
ENV PYTHONUNBUFFERED=1

# Crée un dossier pour ton app
WORKDIR /app

# Copier les fichiers du projet
COPY . .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Port utilisé par Render
EXPOSE 10000

# Commande de lancement
CMD ["gunicorn", "-b", "0.0.0.0:10000", "app:app"]
