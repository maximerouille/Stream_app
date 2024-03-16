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

def voyage_et_affichage(heure_depart, gare_depart, gares_intermediaires, gare_arrivee):
    segments = [gare_depart] + gares_intermediaires + [gare_arrivee]  # Construction de la liste des gares pour chaque segment
    heure_actuelle_depart = heure_depart

    for i in range(len(segments) - 1):
        gare_debut = segments[i]
        gare_fin = segments[i+1]

        date_depart_segment = convertir_en_chaine(heure_actuelle_depart)

        # Requête à l'API pour le segment actuel
        response = requests.get(
            f'https://api.sncf.com/v1/coverage/sncf/journeys?from={gare_debut}&to={gare_fin}&datetime={date_depart_segment}',
            auth=(token_auth, '')
        ).json()

        # Extraction des données du trajet pour le segment actuel
        df_segment = extraire_donnees_trajet(response)
        
        # Affichage du DataFrame du segment actuel
        if not df_segment.empty:
            st.write(f"Segment de {segments[i]} à {segments[i+1]}")
            st.dataframe(df_segment)
            derniere_arrivee = df_segment['Arrivee'].max()
            heure_actuelle_depart = derniere_arrivee + timedelta(minutes=3)  # Ajout d'un délai avant le prochain segment
        else:
            st.write(f"Pas de trajet trouvé de {gare_debut} à {gare_fin}.")

# Interface Streamlit
st.title("FUCK YOU")

# Sélection de la gare de départ et d'arrivée
nom_gare_depart = st.selectbox("Choose the departure station:", df_gares['name'])
nom_gare_arrivee = st.selectbox("Choose the arrival station:", df_gares['name'])

# Identification des gares intermédiaires
options_gares = df_gares['name'].tolist()
gares_intermediaires = st.multiselect('Choose other station you will have to go (optional):', options_gares)

# Conversion des noms en identifiants
id_gare_depart = df_gares[df_gares['name'] == nom_gare_depart]['id'].values[0]
id_gare_arrivee = df_gares[df_gares['name'] == nom_gare_arrivee]['id'].values[0]
ids_gares_intermediaires = [df_gares[df_gares['name'] == nom]['id'].values[0] for nom in gares_intermediaires]

# Widgets pour sélectionner l'heure et la date de départ
heure_depart_utilisateur = st.time_input("What time we go bobo")
date_depart_utilisateur = st.date_input("What day bobo", datetime.now())
datetime_depart = datetime.combine(date_depart_utilisateur, heure_depart_utilisateur)

if st.button("CLICK HEEEEERE... te amo"):
    voyage_et_affichage(datetime_depart, id_gare_depart, ids_gares_intermediaires, id_gare_arrivee)
