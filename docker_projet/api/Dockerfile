FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

# Répertoire de travail dans le conteneur
WORKDIR /my_server/

# Copiez les fichiers requis dans le conteneur
ADD ./api/requirements.txt .
ADD ./api/api_projet.py .
#Ajout d'un script bash vérifiant que l'ETL est bien achevée, et mettant dans le cas contraire en attente le lancement de l'api
ADD ./waiting.sh .
ADD ./api/fonctions_check.py .
RUN chmod +x waiting.sh

# Installez les dépendances Python
RUN apt-get update && apt-get install -y python3-pip && pip3 install --no-cache-dir -r requirements.txt

# Exposez le port sur lequel l'API écoute
EXPOSE 10002

# Commande pour lancer l'API
CMD /bin/bash -c "bash waiting.sh && uvicorn api_projet:api --host 0.0.0.0 --port 10002"