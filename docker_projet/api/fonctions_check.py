#Les fonctions Checkyear, Checkmonth, CheckUri ...
#Sont des fonctions qui prennent en argument le dataframe et l'élément qui sert de filtre et retourne un dataframe pour lequel tous les éléments de la colonne
#correspondantes au filtrage correspond à l'élément de filtrage

#Exemple d'appel : df_filtrer = Checkyear(df, 2023) 
#Ici nous avons en sortie un dataframe avec seulement les colonnes qui ont pour valeurs de year : 2023
def checkyear(df, year):
   df_checked = df.loc[(df['year'] == year)]
   return df_checked

def checkmonth(df, month):
    df_checked = df.loc[(df['month'] == month)]
    return df_checked

def checkUri(df, uri):
    df_checked = df.loc[(df['id_uri'] == uri)]
    return df_checked
   
def checkSection(df, section):
    df_checked = df.loc[(df['section'] == section)]
    return df_checked

def checkSource(df, source):
    df_checked = df.loc[(df['source'] == source)]
    return df_checked

def checkAuthorArticles(df, author):
    return df[df['author'].apply(lambda authors: author in authors)]

def checkTitle(df, title):
    return df.loc[(df['title'] == title)]

def checkAuthor(df, author):
    return df.loc[(df['author'] == author)]

