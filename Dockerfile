# Utiliser l'image officielle Playwright avec Python pré-installé
FROM mcr.microsoft.com/playwright/python:v1.49.0-jammy

# Définir le dossier de travail
WORKDIR /app

# Copier les dépendances
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Installer les navigateurs Playwright (Chromium seulement pour gagner de la place)
RUN playwright install chromium --with-deps

# Copier l'ensemble du projet
COPY . .

# Créer le dossier de configuration avec les bonnes permissions
RUN mkdir -p .config && chmod 700 .config

# Exposer le port de l'API
EXPOSE 8679

# Lancer l'application
CMD ["python", "api.py"]
