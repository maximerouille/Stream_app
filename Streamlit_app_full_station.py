import requests
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta

# URL directe vers le fichier CSV brut sur GitHub
url_csv = 'https://raw.githubusercontent.com/maximerouille/Stream_app/main/Listes_gares.csv'

# Chargement des données des gares depuis GitHub
df_gares = pd.read_csv(url_csv)

# Remplacez 'YOUR_TOKEN_HERE' par votre propre token d'authentification
token_auth = '6d5bd08e-9d01-40b0-a4f0-22adf3490cbc'

def convertir_en_temps(chaine):
    '''Convertit en date la chaîne de caractères de l'API'''
    return datetime.strptime(chaine.replace('T', ' '), '%Y%m%d %H%M%S')

def convertir_en_chaine(dt):
    '''Convertit un datetime en chaîne de caractères au format de l'API'''
    return datetime.strftime(dt, '%Y%m%dT%H%M%S')

def extraire_donnees_trajet(reponse_api):
    '''Extrait les données d'un trajet de la réponse de l'API et les retourne sous forme de DataFrame'''
    rows = []
    for journey in reponse_api['journeys']:
        for section in journey['sections']:
            if "stop_date_times" in section:
                for i in section['stop_date_times']:
                    rows.append(dict(
                        Nom=i['stop_point']['name'],
                        Depart=convertir_en_temps(i['departure_date_time']),
                        Arrivee=convertir_en_temps(i['arrival_date_time'])
                    ))
    return pd.DataFrame(rows)

def voyage(heure_depart, gare_depart, gares_intermediaires, gare_arrivee):
    # Vous devez implémenter cette fonction pour gérer les gares intermédiaires
    pass

# Interface Streamlit
st.title("Calculateur d'itinéraire SNCF avec choix des gares intermédiaires")

# Sélection de la gare de départ et d'arrivée
nom_gare_depart = st.selectbox("Choisissez votre gare de départ:", df_gares['name'])
nom_gare_arrivee = st.selectbox("Choisissez votre gare d'arrivée:", df_gares['name'])

# Widgets pour sélectionner l'heure et la date de départ
heure_depart_utilisateur = st.time_input("Heure de départ souhaitée")
date_depart_utilisateur = st.date_input("Date de départ", datetime.now())
datetime_depart = datetime.combine(date_depart_utilisateur, heure_depart_utilisateur)

# Demande à l'utilisateur s'il souhaite ajouter des gares intermédiaires
ajouter_gares_intermediaires = st.checkbox("Ajouter des gares intermédiaires")

id_gares_intermediaires = []
if ajouter_gares_intermediaires:
    nombre_gares_intermediaires = st.number_input("Combien de gares intermédiaires souhaitez-vous ajouter ?", min_value=0, max_value=5, value=1, step=1)
    for i in range(int(nombre_gares_intermediaires)):
        nom_gare_intermediaire = st.selectbox(f"Gare intermédiaire {i+1} :", df_gares['name'], key=i)
        id_gare_intermediaire = df_gares[df_gares['name'] == nom_gare_intermediaire]['id'].values[0]
        id_gares_intermediaires.append(id_gare_intermediaire)

# Recherche des identifiants des gares sélectionnées
id_gare_depart = df_gares[df_gares['name'] == nom_gare_depart]['id'].values[0]
id_gare_arrivee = df_gares[df_gares['name'] == nom_gare_arrivee]['id'].values[0]

# Affichage de l'heure et de la date choisies pour confirmation
st.write(f"Vous avez choisi de partir le {date_depart_utilisateur} à {heure_depart_utilisateur}.")

# Bouton pour calculer l'itinéraire
if st.button("Calculer l'itinéraire"):
    trajet = voyage(datetime_depart, id_gare_depart, id_gares_intermediaires, id_gare_arrivee)
    st.subheader("Détails du trajet")
    st.dataframe(trajet)
