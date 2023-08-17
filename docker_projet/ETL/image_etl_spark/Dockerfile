#Importation d'une image de base contenant py spark et spark streaming
FROM jupyter/pyspark-notebook:ubuntu-18.04
#Téléchargement des bibliothèques pour éxecuter le script ETL_spark_streaming
USER root
ADD ./ETL/image_etl_spark/requirements.txt .
RUN apt-get update && apt-get install python3-pip -y && pip3 install -r requirements.txt
#Ajout du script python de l'ETL dans un répertoire de travail
ADD ./ETL/etl_spark_streaming.py .
ADD ./configuration.ini .
#Ajout d'un script bash vérifiant que l'ETL est bien achevée, et mettant dans le cas contraire en attente l'éxécution du script python etl_spark_streaming.py
ADD ./waiting.sh .
RUN chmod +x waiting.sh
#Exposition du port du conteneur 
EXPOSE 10001
#Execution du script bash et du script python de l'ETL 
CMD /bin/bash -c "bash waiting.sh && python3 etl_spark_streaming.py"
