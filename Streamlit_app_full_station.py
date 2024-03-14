import requests
import pandas as pd
import streamlit as st
from datetime import datetime

# Fonction pour convertir une chaîne de l'API en datetime
def convertir_en_temps(chaine):
    return datetime.strptime(chaine.replace('T', ''), '%Y%m%d%H%M%S')

# Fonction pour convertir un datetime en chaîne pour l'API
def convertir_en_chaine(dt):
    return datetime.strftime(dt, '%Y%m%dT%H%M%S')

# Fonction pour extraire les données de trajet de l'API
def extraire_donnees_trajet(reponse_api):
    rows = []
    section = reponse_api['journeys'][0]['sections'][1]
    if "stop_date_times" in section:
        for i in section['stop_date_times']:
            rows.append({
                "Nom": i['stop_point']['name'],
                "Depart": convertir_en_temps(i['departure_date_time']),
                "Arrivee": convertir_en_temps(i['arrival_date_time'])
            })
    return pd.DataFrame(rows)

# Fonction principale de calcul d'itinéraire
def voyage(heure_depart, id_gare_depart, id_gare_arrivee):
    token_auth = '6d5bd08e-9d01-40b0-a4f0-22adf3490cbc'
    date_depart = convertir_en_chaine(heure_depart)
    
    # Appel à l'API pour le trajet
    response = requests.get(
        f'https://api.sncf.com/v1/coverage/sncf/journeys?from={id_gare_depart}&to={id_gare_arrivee}&datetime={date_depart}',
        auth=(token_auth, '')
    ).json()
    trajet_df = extraire_donnees_trajet(response)
    return trajet_df

# Chargement et préparation des données des gares
df_gares = pd.read_csv("C:\Users\maxim\Downloads\Listes_gares")
dict_gares = pd.Series(df_gares.id_gare.values, index=df_gares.nom_gare).to_dict()

# Interface Streamlit
st.title("Calculateur d'itinéraire SNCF")

# Sélection des gares de départ et d'arrivée
nom_gare_depart = st.selectbox("Choisissez votre gare de départ :", df_gares['nom_gare'].unique())
nom_gare_arrivee = st.selectbox("Choisissez votre gare d'arrivée :", df_gares['nom_gare'].unique())

# Widgets pour la sélection de la date et de l'heure de départ
date_depart_utilisateur = st.date_input("Date de départ", datetime.now())
heure_depart_utilisateur = st.time_input("Heure de départ souhaitée")
datetime_depart = datetime.combine(date_depart_utilisateur, heure_depart_utilisateur)

# Bouton pour calculer l'itinéraire
if st.button("Calculer l'itinéraire"):
    id_gare_depart = dict_gares[nom_gare_depart]
    id_gare_arrivee = dict_gares[nom_gare_arrivee]
    
    trajet_df = voyage(datetime_depart, id_gare_depart, id_gare_arrivee)
    
    st.subheader(f"Trajet de {nom_gare_depart} à {nom_gare_arrivee}")
    st.dataframe(trajet_df)
