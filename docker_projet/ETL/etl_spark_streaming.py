from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.sql import SparkSession, Row
import requests
from pprint import pprint
from pymongo import MongoClient
import json
from pyspark.sql.functions import substring, concat, lit, split
import os
import configparser
import time

#Initialisation de mes mes instances spark
#Attentes de 60 secondes pour éviter les conflits sur les nombres de requêtes avec l'autre ETL
time.sleep(60)
sc = SparkContext("local[2]", "NEW_Y_TIMES_PROJET")
sc.setLogLevel("ERROR")
ssc = StreamingContext(sc, 30)

spark = SparkSession \
    .builder \
    .master("local") \
    .appName("NEW_Y_TIMES_PROJET") \
    .config("spark.mongodb.input.uri", "mongodb://localhost/db.collection") \
    .config("spark.mongodb.output.uri", "mongodb://localhost/db.collection") \
    .getOrCreate()



#Initialisation des colonnes que nous souhatons conserver
cols = ['abstract', 'byline', 'created_date','item_type', 'published_date','section', 'slug_name','source','title','updated_date','url','uri']
#Intialialisation de la clé de l'API
config = configparser.ConfigParser()
config.read('configuration.ini')
api_key_time_new_wire = str(config['api']['api_key_time_new_wire'])

#Intialisation du client mongo plus de la variable représentant la collection
client = MongoClient(
host=str(os.environ.get('ADDRESSIP')),
port = 27017)
db = client["db_projet"]
collection = db["time_new_wire"]


def extract(key):

  """
  Cette fonction prend la clé de l'API et donne en sortie une liste d'article 

  EXEMPLE D'APPEL : articles = extract(APIKEY])
  """  


  #Utilisation de la library request pour récupérer les éléments de l'URL (code récupérer sur NY TIMES DEVELOPER)

  #Instanciation des variables pour récupérer les données avec l'API
  requestUrl = f"https://api.nytimes.com/svc/news/v3/content/nyt/all.json?api-key={key}&limit=500"
  requestHeaders = {
    "Accept": "application/json"
  }
  response = requests.get(requestUrl, headers=requestHeaders)

  #transformation des données json en JS qui est un fichier manipulable
  #data = response.json()
  data = json.loads(response.text)

  
  #on passe la sous partie results de la réponse obtenue car c'est ici que se trouve les articles
  articles = data.get("results")
  
  #Boucle qui permet d'insérer à chaque passage le nouvelle article 
  for article in articles:
    selected = {k: article.get(k,"") for k in cols}
    yield selected


def transform(df):
  """
  Cette fonction prend un dataframe et crée un id à partir de la colonne uri

  EXEMPLE D'APPEL : transform(df)
  
  """
  #Ajoute de la colonne text_split, colonne qui vas séparer par un espace le 15 caractère de la chaine présente dans URI
  df = df.withColumn("text_split", concat(substring("uri", 0, 15), lit(" "), substring("uri", 15, 100)))

  #Création de la colonne col_split qui vas être un tableau avec en élément 1 la parti correspondant à l'ID 
  df = df.withColumn("col_split", split(df["text_split"], ' '))

  #Création de la colonne id_uri qui est l'id de l'article en fonction de l'uri, l'uri est unique pour chaque article
  df = df.withColumn('id_uri', df['col_split'].getItem(1))

  #Nous supprimer les colonnes inutulisables
  df = df.drop("text_split")
  df = df.drop("col_split")
  df = df.drop("uri")

  df.printSchema()


def load(df, collection):
  """
  Cette fonction prend en entrée un dataframe et une collection et charge le dataframe dans la collection

  exemple d'appel : load(df,collection)
  """

  #collect des ligne du dataframe
  rows = df.collect()  

  #transformation de rows en dictionnaire pour le chargeent
  articles = [row.asDict() for row in rows]

  #Boucle qui charge les données 
  for article in articles:
    collection.insert_one(article)




#Mise en place de la queue stream en écoute sur la fonction extract
dstream = ssc.queueStream([extract(api_key_time_new_wire)])


def processData(rdd):    
  if not rdd.isEmpty():
        #récupération des lignes du rdd pour la création d'un dataframe
        rows = [Row(**k) for k in rdd.collect()]
        #création du datafram
        df = spark.createDataFrame(rows)
        #appel de la fonction transfrom
        transform(df)
        df.show()
        #appel de la fonction load
        load(df, collection)
  else: 
        print('le RDD est vide voir la partie extraction !')


dstream.foreachRDD(processData)


ssc.start()
ssc.awaitTermination()


pprint(extract(key, section))