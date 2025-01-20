# Utiliser une image de base Python
FROM python:3.11-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier le fichier requirements.txt et installer les dépendances
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Définir un répertoire dédié pour les données NLTK
ENV NLTK_DATA=/app/nltk_data


# Copier tout le projet dans le conteneur
COPY . /app

# Exposer le port utilisé par Streamlit
EXPOSE 8501

# Commande pour exécuter l'application Streamlit
CMD ["sh", "-c", "PYTHONPATH=/app/src streamlit run src/app/app.py --server.port=8501 --server.address=0.0.0.0"]
