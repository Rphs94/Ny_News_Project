import requests
import json
from pprint import pprint
import time
from pymongo import MongoClient
import os
import configparser

#L'ETL de ce script extrait,transforme et charge les données des trois API du projet NY news dans une base de données MongoDB
#Fonctions d'EXTRACTION

#initialisation des clés api à partir d'un fichier configuration.ini
config = configparser.ConfigParser()
config.read('configuration.ini')
api_key_time_new_wire = str(config['api']['api_key_time_new_wire'])
api_key_books = str(config['api']['api_key_books'])
api_key_article_search = str(config['api']['api_key_article_search'])

#Extraction de l'API Books
def extract_books():
    """
    Cette fonction ne prend pas d'argument en entrée. La sortie de cette fonction est une liste d'objets json obtenue en requêtant l'API Books du New York Times.
    """

    #clé API Books
    global api_key_books
    
    url = requests.get(f'https://api.nytimes.com/svc/books/v3/lists/full-overview.json?api-key={api_key_books}')
    link = url.json()
    source = link["results"]["lists"] #naviguation a la suite dans les clé "results" et "list"
    
    #création dans une liste de tout les livres
    books = []
    for i in source:
        for a in i['books']:
            books.append(a)

    return books


#Extraction de l'API Article Search
def extract_article_search(section) :
    """
    Cette fonction prend en argument une liste de section et renvoie 100 articles par sections.
    Le résultats retourné est une liste d'objet au format json.
    L'API impose une limite jusqu'à 200 pages par catégorie.
    L'API impose aussi une limite de 10 requête par minutes.
    """
    global api_key_article_search
    data_article=[]
    for cate in section :
        
        params={
            "q" : cate,
            "page":1,
            "api-key":api_key_article_search
        }
        query = cate
        #url de l'API 
        base_url = f"https://api.nytimes.com/svc/search/v2/articlesearch.json?"
        response = requests.get(base_url,params)
        #variable data de type dictionnaire contenant les informations obtenus grâce à la librairie requests
        data = response.json()
        
        # data variable de type dictionnaire avec trois clés : ['status', 'copyright', 'response']
        response=data["response"]
        #data["reponse"] contient les clés ['docs', 'meta']
        docs=response["docs"]
        
        data_article=data_article+docs
            
            
    
    return data_article

    
#Extraction de l'API Times new wire
def extract_time_new_wire(listSections, key):
  """
  Fonction qui donne en sortie une liste de fichier JSON correspondant à 500 articles (taille de données maximale) de chaque sections passées en paramètre
  EXEMPLE D'APPEL : list_JSON = create_json_files(listSections, key)
  """

  def getarticle(key, section):

    """
    Cette fonction prend la clé de l'API et une section et donne en sortie une liste d'article correspondant à la section
    EXEMPLE D'APPEL : articles = getArticles(APIKEY, sections[1])
    """  

    #Nous recupérons nos articles directement du new york times
    nyt = "nyt"

    #Utilisation de la library request pour récupérer les éléments de l'URL (code récupérer sur NY TIMES DEVELOPER)

    #Instanciation des variables pour récupérer les données avec l'API
    requestUrl = f"https://api.nytimes.com/svc/news/v3/content/{nyt}/{section}.json?api-key={key}&limit=500"
    requestHeaders = {
        "Accept": "application/json"
    }
    response = requests.get(requestUrl, headers=requestHeaders)

    #transformation des données json en JS qui est un fichier manipulable
    data = response.json()

    #on passe la sous partie results de la réponse obtenue car c'est ici que se trouve les articles
    results = data["results"]
    
    
    
    return results

  #création d'une liste vide qui sera retourner par la fonction
  list_json = []

  #Iération sur chaque section
  for section in listSections:

     #recupération de la liste d'article de chaque section 
     list_art = getarticle(key, section)
     
     #ajout de la liste d'article dans un liste 
     list_json=list_json+list_art


  for element in list_json:
    col_splited = element['published_date'].split('-')
    element['year'] = col_splited[0]
    element['month'] = col_splited[1]
 
  return list_json




#TRANSFORMATION
#Transformation books
#netoyage du code en retirant les clés qui ne sont pas necesaire
def transformation_books(data_books):
    cleaner = ['age_group', 'amazon_product_url', 'article_chapter_link', 'book_image','book_image_width', 'book_image_height', 'book_review_link', 'book_uri', 'contributor', 'contributor_note', 'created_date', 'first_chapter_link', 'price', 'rank', 'rank_last_week', 'sunday_review_link', 'updated_date', 'weeks_on_list']
    for book in data_books:
        for i in cleaner:
            book.pop(i)
    return data_books

#Transformation Article_search 
def transformation_article_search(data):
    
    remove=['multimedia','snippet','uri']
    for article in data :
        for y in remove :
            article.pop(y)
        
        #recupération du nom et prénom des auteurs de l'article dans une clé author
        article["byline"].pop("organization")
        article["byline"].pop("original")
        article["author"]=[]

        for author in (article["byline"]["person"]):
            name=""
            for nom in [author["firstname"],author["middlename"],author["lastname"]]:
                
                if type(nom)==str:
                    name= name+" "+nom
            article["author"].append(name)
        
        #suppression de la clé byline de article contenant les informations sur les auteurs après extraction vers la clé author
        article.pop("byline")

        col_splited = article['pub_date'].split('-')
        article['year'] = col_splited[0]
        article['month'] = col_splited[1]

        #extraction du résumé  print_headline
        
        for cle in ['content_kicker','kicker','main','name','seo','sub'] :
            article["headline"].pop(cle)
        article["headline"]=article["headline"]["print_headline"]
        

        #extraction des keywords
        mot=[]
        for keywords in article["keywords"] :
            mot.append(keywords["value"])
        
        article["keywords"]=mot
        

    return data

###EXTRACTION
#Les résultats de cette extraction sont contenues dans la variable data_books qui est une liste d'objets json
data_books=extract_books()

#Définition des sections que nous allons récupérer pour la base de données
section=["Business","Education","Health","Food","Science"]

#Les résultats de cette extraction sont contenues dans la variable data_article_search qui est une liste d'objets json
data_article_search=extract_article_search(section)

#Liste de sections dont les articles sont à extraire
listsections = ['business', 'education', 'health','science','movies']
#Appel de la fonction d'ingestion
data_time_new_wire=extract_time_new_wire(listsections,api_key_time_new_wire)

###TRANSFORMATION

data_books=transformation_books(data_books)
#Transformation des articles extrait de l'API article Search
data_article_search=transformation_article_search(data_article_search)

#transformation Times new wire

#creation d'une liste avec les colonnes qui seront supprimés pour chaque article
cols = ['multimedia','thumbnail_standard','geo_facet','per_facet','org_facet','des_facet','related_urls','short_url','subheadline']

#Boucle pour supprimer les colonnes 
for article in data_time_new_wire:
    article = [article.pop(c, None) for c in cols]
  
#CHARGEMENT
client = MongoClient(
    host=str(os.environ.get('ADDRESSIP')),
    port = 27017, 
)

#Cration de la base de données commune db_projet
db=client["db_projet"]
#Création des différentes collection et chargement des données dans celles-ci
#Books
books=db["books"]
for i in data_books:
        books.update_one({'_id': i['primary_isbn13']}, {'$set': i}, upsert=True)



#Article Search
articles_search=db["articles_search"]

#Si le document existe déja, mise à jour de celui, sinon insertion du nouveau document dans la collection articles
for document in data_article_search:
    articles_search.update_one({'_id': document['_id']}, {'$set': document}, upsert=True)

#Times new wire

time_new_wire=db["time_new_wire"]
for article in data_time_new_wire:
    time_new_wire.update_one({'_id': article['uri']}, {'$set': article}, upsert=True)
