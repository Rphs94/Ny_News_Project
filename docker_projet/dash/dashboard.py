import dash
from dash import dcc
from dash import html
import pandas as pd
from dash.dependencies import Output,Input
from dash import dash_table
import plotly.graph_objects as go
import requests
import time
import os


ADDRESSIP=str(os.environ.get('ADDRESSIP'))


#Style graphique pour le dashboard 
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets,suppress_callback_exceptions=True)

#Crétion de la page d'accueil avec trois boutons menant chacun à une page, une par api
app.layout = html.Div([
     
    dcc.Location(id='url', refresh=False),
   
    html.Div(id='page-content')
], style={'alignItems': 'center'})

#Création de la page d'accueil et des différents composants de celle-ci
index_page = html.Div([
    html.H1('Dashboard project NY news', style={'color' : 'mediumturquoise', 'textAlign': 'center'}),
    html.Br(),
    html.Br(),
    html.Button(
    dcc.Link('Books', href='/page-1'),
    style={'border': '2px solid mediumturquoise', 'border-radius': '5px'}),  
    html.Br(),
    html.Br(),
    html.Button(
    dcc.Link('Times New Wire', href='/page-2'),
    style={'border': '2px solid mediumturquoise', 'border-radius': '5px'}),
    html.Br(),
    html.Br(),
    html.Button(
    dcc.Link('Article Search', href='/page-3'),
    style={'border': '2px solid mediumturquoise', 'border-radius': '5px'})
    
])

#Attente de connexion avec l'api
while True:
    try:
        response = requests.get(f"http://{ADDRESSIP}:10002/Articles_search")
        if response.status_code == 200:
            break  
    except requests.exceptions.ConnectionError:
        pass  
    
    print("Waiting for connection with the API...")
    time.sleep(1)


#Page Books

#Obtention des noms de colonnes pour la datatable 
response=requests.get(f"http://{ADDRESSIP}:10002/books")
data=response.json()
columns=list(data[0].keys())
L=[]
remove=["_id"]
L = [col for col in columns if col not in remove]


#Création des dataframes en fonction des collections
df_books = pd.DataFrame(data, columns=L)

#Création du Layout pour l'application Books
layout_1 = html.Div([

              #Affichage du titre
        html.H1("Search in our Books dataset", style={"margin-bottom": "30px"}),


        #Input qui contiendra le titre du livre souhaité
        dcc.Input(
            id="search-input-1",
            type="text",
            placeholder="Title of the book you are looking for...",
            style={"width": "10%",  "margin-right": "25px"}
        ),

        html.P(
            children = "DESCRIPTION : ",
            id="my-text2",
            style = {"margin-top": "50px"}
        ),


        #Paragraph qui affichera une description du livre
        html.P(
            children = "Le livre n'est pas présent dans la base",
            id="my-text",
            style = {"margin-top": "20px"}
        ),

        html.P(
            children = "URL FOR PURCHASE : ",
            id="my-text2",
            style = {"margin-top": "50px"}
        ),

        #Lien qui redirigera vers une page qui nous permet d'acheter le livre
        html.Div(dcc.Link(
            children = "", 
            href="", 
            id="my-link",
            style={"width": "15%", "margin-right": "500px", "margin-bottom": "20px",  "margin-top": "15px"} 
            ),
             style={"margin-top": "20px"} 
        ),

        #Bouton pour revenir à la page d'accueil
        html.Div(html.Button(dcc.Link('Return to home page', href='/'), style={ "margin-top": "50px", "margin-bottom": "20px"}))
])


#Définition du callback qui affiche le lien
@app.callback(
            Output(component_id='my-link', component_property='children'),
            [Input(component_id='search-input-1', component_property='value')]
            )
def update_url(element):

    filtered_df = df_books[df_books['title'].str.casefold() == element.casefold()]
    if not filtered_df.empty:
        url = filtered_df.loc[filtered_df.index[0], "buy_links"][0]["url"]
        print(":",url)
    else:
        return ("")

    return url


#Définition du callback qui crée le lien vers la page d'achat
@app.callback(
            Output(component_id='my-link', component_property='href'),
            [Input(component_id='search-input-1', component_property='value')]
            )
def update_href(element):
    url=""
    filtered_df = df_books[df_books['title'].str.casefold() == element.casefold()]
    if not filtered_df.empty:
        url = filtered_df.loc[filtered_df.index[0], "buy_links"][0]["url"]


    return url


#Call afin d'afficher correctement la description
@app.callback(
            Output(component_id='my-text', component_property='children'),
            [Input(component_id='search-input-1', component_property='value')]
            )
def update_description(element):

    description = df_books[(df_books['title'].str.casefold() == element.casefold())]['description']

     #agregation pour récupérer la description
    if len(description) == 0:
        return "the book is not present in the database"
    
    

    return description


#Page Time new wire

#Obtention des noms de colonnes pour la datatable 
response=requests.get(f"http://{ADDRESSIP}:10002/new_times_wire")
data=response.json()
columns=list(data[0].keys())
L=[]
remove=["_id"]
L = [col for col in columns if col not in remove]


#Création du dataframe en fonction de la collections
df_time_wire = pd.DataFrame(data, columns=L)

dictionary_returned = df_time_wire[['title', 'section','abstract', 'url']].fillna("N/A").to_dict('records')

for line in dictionary_returned:
    line["url"] = f'[{line["url"]}]({line["url"]})'


#CREATION DE LA FIGURE AVEC L'AGGREGATION
df_count_year = df_time_wire['year'].value_counts().rename_axis('col_index').reset_index(name='count')
df_count_section = df_time_wire['section'].value_counts().rename_axis('col_index').reset_index(name='count')

# Initilialisation des x et y
x = df_count_section['col_index']
y = df_count_section['count']

x2 = df_count_year['col_index'].head(3)
y2 = df_count_year['count'].head(3)


#Conversion du graphique Matplotlib en objet Figure de Plotly
fig = go.Figure(data=[go.Bar(x=x2, y=y2, name = 'Années'), go.Bar(x=x, y=y, name = 'Sections')])

fig.update_layout(
    title="Fréquence des Années et Sections dans notre jeu de données",
    yaxis=dict(title="Fréquence")
)


layout_2 = html.Div([
   
    #Bouton pour revenir à la page d'accueil
    html.Button(dcc.Link('Return to home page', href='/')),


    html.H1("Visualizing Our Dataset New Times Wire"),
     
    
    #Définition du graphe qui sera le bar plot
    html.Div(dcc.Graph(figure=fig)),

    #Création de la zone de recherche pour le tableau
    dcc.Input(
            id="search-input",
            type="text",
            placeholder="",
            style={"width": "15%",  "margin-bottom": "20px"},
            ),
  
    #Instanciation qui représente le tableau
    dash_table.DataTable(
        id = "table-page-1",
        columns=[
                {'name': 'Title', 'id': 'title'},
                {'name': 'Section', 'id': 'section'},
                {'name': 'Abstract', 'id': 'abstract'},
                {'name': 'URL', 'id': 'url', 'type': 'text', "presentation": "markdown"}
            ],
        data = dictionary_returned,
        style_cell={
        'textAlign': 'center',  
        'minWidth': '120px',    
        'width': '120px',       
        'maxWidth': '300px',    
        'whiteSpace': 'normal', 
        'overflow': 'hidden',   
        'textOverflow': 'ellipsis',  
        },
        style_data={
        'whiteSpace': 'normal',  
        'overflow': 'hidden',    
        'textOverflow': 'ellipsis',   
        }
    )
])



#Callback qui modifie le tableau en fonction du titre d'article ou de la section mise en paramètre
@app.callback(Output(component_id='table-page-1', component_property='data'),
            [Input(component_id='search-input', component_property='value')])
def update_table(text):

    filtered_df = df_time_wire[(df_time_wire['section'] == text).fillna("N/A") | (df_time_wire['title'] == text).fillna("N/A")]

    if not filtered_df.empty:

        dictionary_returned = filtered_df[['title', 'section', 'abstract', 'url']].to_dict('records')

        for line in dictionary_returned:
            line["url"] = f'[{line["url"]}]({line["url"]})'

        return dictionary_returned

    else:

      dictionary_returned = df_time_wire[['title', 'section','abstract', 'url']].fillna("N/A").to_dict('records')

      for line in dictionary_returned:
        line["url"] = f'[{line["url"]}]({line["url"]})'
        
      return dictionary_returned




#Page Article Search

#Obtention des noms de colonnes pour la datatable 
response=requests.get(f"http://{ADDRESSIP}:10002/Articles_search")
data=response.json()
columns=list(data[0].keys())
L=[]
remove=["_id","month","source","news_desk","print_page","print_section","word_count","document_type","type_of_material","pub_date","lead_paragraph","headline","subsection_name","web_url"]
for col in columns:
    if col not in remove :
        L.append(col)

#Layout de la page Article Search
layout_3 = html.Div([
    html.H1('Article Search', style={'textAlign': 'center', 'color': 'mediumturquoise'}),
    html.Button(dcc.Link('Go back to the main page', href='/'),style = {'background' : 'beige'}),

    html.Div([
        html.Br(),
        html.Br(),
        html.Label('Please enter an author, publication year, keyword or specific section in the search engine', style={'color': 'black', 'font-size': '16px','font-style': 'italic'}),
        #Création d'un moteur de recherche permettant de filtrer par annéee, nom d'auteur, section, ou mots-clés
        dcc.Input(
            id = 'search_engine',
            value = '', 
            type = "text",
            style={'color': 'black', 'font-size': '16px','font-style': 'italic'}
            ),
    html.Br(),
    html.Br(),
    #Création d'une table avec tous les articles de article search de la base de données
    html.Div([
    dash_table.DataTable(
        id='datatable_article_search',
        columns=[{'name': col, 'id': col} for col in L]+[{'name':'web_url','id':'web_url',"type": "text", "presentation": "markdown"}],
        data=[],
        style_cell={
        'textAlign': 'center',  
        'minWidth': '120px',    
        'width': '120px',       
        'maxWidth': '300px',    
        'whiteSpace': 'normal', 
        'overflow': 'hidden',   
        'textOverflow': 'ellipsis',  
    },
    style_data={
        'whiteSpace': 'normal',  
        'overflow': 'hidden',    
        'textOverflow': 'ellipsis',   
    }
        
    )
])

])
])

@app.callback(Output(component_id='datatable_article_search', component_property='data'),
            [Input(component_id='search_engine', component_property='value')])
def update_data(texte):
    #Affichage de tous les articles si pas de requête dans le moteur de recherche
    if texte=='':
        response=requests.get(f"http://{ADDRESSIP}:10002/Articles_search")
        data=response.json()
        #Traitement de la données pour la rendre conforme à la datatablee dash, celle-ci n'accepte que des données de type string, int ou booléen
        for article in data:
            article["web_url"] = f'[{article["web_url"]}]({article["web_url"]})'
            authors=""
            keys=""
            for author in article["author"]:
                authors=authors+","+author
            article["author"]=authors[1:]
            for key in article["keywords"]:
                keys=keys+","+key
            article["keywords"]=keys[1:]
        return data
    #Affichage des articles filtrer par le moteur de recherche 
    else :
            url=f"http://{ADDRESSIP}:10002/Articles_search?"
            response=requests.get(url)
            data=response.json()
            list_article=[]
            for article in data :
                article["web_url"] = f'[{article["web_url"]}]({article["web_url"]})'
                if texte.casefold()==article["section_name"].casefold() or texte==article["year"]:
                    authors=""
                    keys=""
                    for author in article["author"]:
                        authors=authors+","+author
                    article["author"]=authors[1:]
                    for key in article["keywords"]:
                        keys=keys+","+key
                    article["keywords"]=keys[1:]
                    list_article.append(article)
                else :
                    for keyword in article["keywords"]:
                        if texte.casefold()==keyword.casefold():
                            authors=""
                            keys=""
                            for author in article["author"]:
                                authors=authors+","+author
                            article["author"]=authors[1:]
                            for key in article["keywords"]:
                                keys=keys+","+key
                            article["keywords"]=keys[1:]
                            list_article.append(article)
                            break
                    
                    for author in article["author"]:
                        if " "+texte.casefold()==author.casefold():
                            authors=""
                            keys=""
                            for author in article["author"]:
                                authors=authors+","+author
                            article["author"]=authors[1:]
                            for key in article["keywords"]:
                                keys=keys+","+key
                            article["keywords"]=keys[1:]
                            list_article.append(article)
                            break
            return list_article


        
        


#Gestion de l'interaction entre les boutons et l'utilisateur pour accéder à la page d'accueil ou aux différentes pages de chaque api
@app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/page-1':
        return layout_1
    elif pathname == '/page-2':
        return layout_2
    elif pathname == '/page-3':
        return layout_3
    else:
        return index_page



if __name__ == '__main__':
    app.run_server(debug=True,host="0.0.0.0",port = 10003)