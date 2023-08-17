import pandas as pd 
from fastapi import FastAPI
from fastapi import HTTPException
from typing import Optional
from pymongo import MongoClient
from fonctions_check import checkyear, checkmonth, checkUri, checkSection, checkSource, checkAuthorArticles, checkTitle, checkAuthor
import os 


#Initialisation de la variable API pour faire appel au framework
api = FastAPI()

#Intialisation du client mongo plus de la variable représentant la collection
client = MongoClient(
    host=str(os.environ.get('ADDRESSIP')),
    port = 27017)
db = client["db_projet"]

#initialisation des collections
collection_times_wire = db["time_new_wire"]
collection_books = db["books"]
collection_articles_search = db["articles_search"]

#Création des dataframes en fonction des collections
df_time_wire = pd.DataFrame(list(collection_times_wire.find()))
df_books = pd.DataFrame(list(collection_books.find()))
df_articles_search = pd.DataFrame(list(collection_articles_search.find())).fillna({'subsection_name': 'Valeurs inconnues', 'headline': 'Valeurs inconnues','print_page': 'Valeurs inconnues','print_section': 'Valeurs inconnues' })



@api.get('/new_times_wire')
def get_time_wire_articles(year: Optional[str]=None, month: Optional[str]=None, uri:Optional[str]=None, section: Optional[str]=None, source: Optional[str]=None):

    df_checked = df_time_wire

    if  uri:
        df_checked = checkUri(df_checked, uri)

        if df_checked.empty:
            return {"erreur : L'uri n'est pas dans la base de données"}

    if  year:
        df_checked = checkyear(df_checked, year)

        if df_checked.empty:
            return {"erreur : L'année n'est pas dans la base de données"}

    if  month:
        df_checked = checkmonth(df_checked, month)

        if df_checked.empty:
            return {"erreur : Le month n'est pas dans la base de données"}

    if section:
        df_checked = checkSection(df_checked, section)

        if df_checked.empty:
            return {"erreur : La section n'est pas dans la base de données"}

    if source:
        df_checked = checkSource(df_checked, source)

        if df_checked.empty:
            return {"erreur : La source n'est pas dans la base de données"}


    return df_checked.to_dict(orient='records')



@api.get('/books')
def get_books(title: Optional[str]=None, author: Optional[str]=None):

    df_checked = df_books

    if title:
        df_checked = checkTitle(df_checked, title)

        if df_checked.empty:
            return {"erreur : Le titre n'est pas dans la base de données"}
    
    if author:
        df_checked = checkAuthor(df_checked, author)

        if df_checked.empty:
            return {"erreur : L'auteur n'est pas dans la base de données"}

    
   

    return df_checked.to_dict(orient='records')




@api.get('/Articles_search')
def get_Articles_search(year: Optional[str]=None, month: Optional[str]=None, source: Optional[str]=None, author: Optional[str]=None):

    df_checked = df_articles_search

    if year:
        df_checked = checkyear(df_checked, year)

        if df_checked.empty:
            return {"erreur : L'année n'est pas dans la base de données"}

    if  month:
        df_checked = checkmonth(df_checked, month)

        if df_checked.empty:
            return {"erreur : Le month n'est pas dans la base de données"}

    if author:
        df_checked = checkAuthorArticles(df_checked, author)

        if df_checked.empty:
            return {"erreur : L'auteur n'est pas dans la base de données"}
        
    if source:
        df_checked = checkSource(df_checked, source)

        if df_checked.empty:
            return {"erreur : La source n'est pas dans la base de données"}

    
    return df_checked.to_dict(orient='records')