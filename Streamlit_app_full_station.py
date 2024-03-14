import requests
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta

# URL directe vers le fichier CSV brut sur GitHub
url_csv = 'https://raw.githubusercontent.com/yourusername/yourrepository/main/gares.csv'

# Chargement des données des gares depuis GitHub
df_gares = pd.read_csv(url_csv)

# Remplacez 'YOUR_TOKEN_HERE' par votre propre token d'authentification
token_auth = '6d5bd08e-9d01-40b0-a4f0-22adf3490cbc'

def convertir_en_temps(chaine):
    '''Convertit en date la chaîne de caractères de l'API'''
    return datetime.strptime(chaine.replace('T', ''), '%Y%m%d%H%M%S')

def convertir_en_chaine(dt):
    '''Convertit un datetime en chaîne de caractères au format de l'API'''
    return datetime.strftime(dt, '%Y%m%dT%H%M%S')

def extraire_donnees_trajet(reponse_api):
    '''Extrait les données d'un trajet de la réponse de l'API et les retourne sous forme de DataFrame'''
    rows = []
    section = reponse_api['journeys'][0]['sections'][1]
    if "stop_date_times" in section:
        for i in section['stop_date_times']:
            rows.append(dict(
                Nom=i['stop_point']['name'],
                Depart=convertir_en_temps(i['departure_date_time']),
                Arrivee=convertir_en_temps(i['arrival_date_time'])
            ))
    return pd.DataFrame(rows)

def voyage(heure_depart, gare_depart, gare_arrivee):
    date_depart = convertir_en_chaine(heure_depart)

    response = requests.get(
        f'https://api.sncf.com/v1/coverage/sncf/journeys?from={gare_depart}&to={gare_arrivee}&datetime={date_depart}',
        auth=(token_auth, '')
    ).json()
    df_trajet = extraire_donnees_trajet(response)

    return df_trajet

# Interface Streamlit
st.title("Calculateur d'itinéraire SNCF")

# Sélection de la gare de départ et d'arrivée
nom_gare_depart = st.selectbox("Choisissez votre gare de départ:", df_gares['nom'])
nom_gare_arrivee = st.selectbox("Choisissez votre gare d'arrivée:", df_gares['nom'])

# Recherche des identifiants des gares sélectionnées
id_gare_depart = df_gares[df_gares['nom'] == nom_gare_depart]['id'].values[0]
id_gare_arrivee = df_gares[df_gares['nom'] == nom_gare_arrivee]['id'].values[0]

# Widgets pour sélectionner l'heure et la date de départ
heure_depart_utilisateur = st.time_input("Heure de départ souhaitée")
date_depart_utilisateur = st.date_input("Date de départ", datetime.now())
datetime_depart = datetime.combine(date_depart_utilisateur, heure_depart_utilisateur)

# Affichage de l'heure et de la date choisies pour confirmation
st.write(f"Vous avez choisi de partir le {date_depart_utilisateur} à {heure_depart_utilisateur}.")

if st.button("Calculer l'itinéraire"):
    trajet = voyage(datetime_depart, id_gare_depart, id_gare_arrivee)
    st.subheader("Détails du trajet")
    st.dataframe(trajet)
