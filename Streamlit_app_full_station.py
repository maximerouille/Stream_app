import requests
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta

# URL directe vers le fichier CSV brut sur GitHub
url_csv = 'https://raw.githubusercontent.com/maximerouille/Stream_app/main/Listes_gares.csv'

# Chargement des données des gares depuis GitHub
df_gares = pd.read_csv(url_csv)

# Remplacez 'YOUR_TOKEN_HERE' par votre propre token d'authentification
token_auth = '6d5bd08e-9d01-40b0-a4f0-22adf3490cbc'  # Assurez-vous de mettre votre token d'authentification ici

def convertir_en_temps(chaine):
    '''Convertit en date la chaîne de caractères de l'API'''
    return datetime.strptime(chaine, '%Y%m%dT%H%M%S')

def convertir_en_chaine(dt):
    '''Convertit un datetime en chaîne de caractères au format de l'API'''
    return datetime.strftime(dt, '%Y%m%dT%H%M%S')

def extraire_donnees_trajet(reponse_api):
    '''Extrait les données d'un trajet de la réponse de l'API et les retourne sous forme de DataFrame'''
    rows = []
    for section in reponse_api['journeys'][0]['sections']:
        if "stop_date_times" in section:
            for i in section['stop_date_times']:
                rows.append({
                    "Nom": i['stop_point']['name'],
                    "Depart": convertir_en_temps(i['departure_date_time'])
                })
    return pd.DataFrame(rows)

def calculer_voyage_arrivee(heure_arrivee, gare_depart, gare_arrivee):
    date_arrivee_chaine = convertir_en_chaine(heure_arrivee)
    
    response = requests.get(
        f'https://api.sncf.com/v1/coverage/sncf/journeys?from={gare_depart}&to={gare_arrivee}&datetime={date_arrivee_chaine}&datetime_represents=arrival',
        auth=(token_auth, '')
    ).json()

    df_trajet = extraire_donnees_trajet(response)
    if not df_trajet.empty:
        heure_de_depart = df_trajet['Depart'].min()
        st.write(f"We have to leave at : {heure_de_depart.strftime('%H:%M')}, We will arrive at : {heure_arrivee.strftime('%H:%M')}")
        st.write("Some details :")
        st.dataframe(df_trajet[['Nom', 'Depart']])
    else:
        st.write("FOUND NADA")

# Interface Streamlit
st.title("For you bobo TE AMO")

nom_gare_depart = st.selectbox("WHERE IS THE STATION WE TAKE :", df_gares['name'])
nom_gare_arrivee = st.selectbox("WHERE WE ARRIVE :", df_gares['name'])

id_gare_depart = df_gares[df_gares['name'] == nom_gare_depart]['id'].values[0]
id_gare_arrivee = df_gares[df_gares['name'] == nom_gare_arrivee]['id'].values[0]

heure_arrivee_utilisateur = st.time_input("WHAT TIME WE ARRIVE AAAAAAAAAA ?", datetime.now())
date_arrivee_utilisateur = st.date_input("Which day ?", datetime.now())
datetime_arrivee = datetime.combine(date_arrivee_utilisateur, heure_arrivee_utilisateur)

if st.button("CLIIICK AQUI !!!!"):
    calculer_voyage_arrivee(datetime_arrivee, id_gare_depart, id_gare_arrivee)
