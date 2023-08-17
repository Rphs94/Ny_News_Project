FROM python:latest

# Copiez les fichiers requis dans le conteneur
ADD ./dash/requirements.txt .
ADD ./dash/dashboard.py .

#Ajout d'un script bash vérifiant que l'ETL est bien achevée, et mettant dans le cas contraire en attente le lancement de l'api
ADD ./waiting.sh .
RUN chmod +x waiting.sh

# Installez les dépendances Python
RUN apt-get update && apt-get install python3-pip -y && pip3 install -r requirements.txt

# Exposez le port sur lequel l'API écoute
EXPOSE 10003

# Commande pour lancer l'API
CMD /bin/bash -c "bash waiting.sh && python3 dashboard.py"