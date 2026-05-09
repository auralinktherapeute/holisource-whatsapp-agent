# Dockerfile pour Holisource WhatsApp Agent
FROM python:3.11-slim

WORKDIR /app

# Installa dépendances système
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copie les requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie le code de l'application
COPY . .

# Expose le port (dynamique depuis PORT env var)
EXPOSE 8000

# Comando de démarrage - utilise la variable PORT d'environnement
CMD ["sh", "-c", "uvicorn agent.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
