#Importation d'une image de base python
FROM python:latest
#Téléchargement des bibliothèques pour éxecuter le script ETL
ADD ./ETL/image_etl/requirements.txt .
RUN apt-get update && apt-get install python3-pip -y && pip3 install -r requirements.txt
#Ajout du script python de l'ETL dans un répertoire de travail
ADD ./ETL/ETL_NY_news.py /ETL/ETL_NY_news.py
ADD ./configuration.ini /ETL/configuration.ini
WORKDIR /ETL/
#Exposition du port du conteneur 
EXPOSE 10000
#Execution du script python de l'ETL et création d'un marqueur indiquant que l'etl est bien terminé pour les autres conteneurs
CMD python3 ETL_NY_news.py && touch /home/check/finish.txt

