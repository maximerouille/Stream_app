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
                    "Depart": convertir_en_temps(i['departure_date_time']),
                    "Arrivee": convertir_en_temps(i['arrival_date_time'])
                })
    return pd.DataFrame(rows)

# Nouvelle fonction pour calculer et afficher le trajet
def calculer_voyage_arrivee(heure_arrivee, gare_depart, gare_arrivee):
    # Conversion de l'heure d'arrivée souhaitée en format de chaîne accepté par l'API
    date_arrivee_chaine = convertir_en_chaine(heure_arrivee)
    
    # Requête à l'API pour le trajet
    response = requests.get(
        f'https://api.sncf.com/v1/coverage/sncf/journeys?from={gare_depart}&to={gare_arrivee}&datetime={date_arrivee_chaine}&datetime_represents=arrival',
        auth=(token_auth, '')
    ).json()

    # Extraction et affichage des données du trajet
    df_trajet = extraire_donnees_trajet(response)
    if not df_trajet.empty:
        st.write(f"Pour arriver à {gare_arrivee} à {heure_arrivee.strftime('%H:%M')}, vous devez partir de {gare_depart} à:")
        st.dataframe(df_trajet)
    else:
        st.write("Désolé, aucun trajet trouvé.")

# Interface Streamlit
st.title("Planificateur de voyage SNCF")

# Sélection de la gare de départ et d'arrivée
nom_gare_depart = st.selectbox("Choisissez votre gare de départ :", df_gares['name'])
nom_gare_arrivee = st.selectbox("Choisissez votre gare d'arrivée :", df_gares['name'])

# Conversion des noms en identifiants
id_gare_depart = df_gares[df_gares['name'] == nom_gare_depart]['id'].values[0]
id_gare_arrivee = df_gares[df_gares['name'] == nom_gare_arrivee]['id'].values[0]

# Widget pour sélectionner l'heure d'arrivée souhaitée
heure_arrivee_utilisateur = st.time_input("À quelle heure souhaitez-vous arriver ?", datetime.now())
date_arrivee_utilisateur = st.date_input("Quel jour souhaitez-vous arriver ?", datetime.now())
datetime_arrivee = datetime.combine(date_arrivee_utilisateur, heure_arrivee_utilisateur)

if st.button("Planifier mon voyage"):
    calculer_voyage_arrivee(datetime_arrivee, id_gare_depart, id_gare_arrivee)
