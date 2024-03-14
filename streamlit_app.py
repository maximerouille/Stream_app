import requests
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta

# Remplacez 'YOUR_TOKEN_HERE' par votre propre token d'authentification
token_auth = '6d5bd08e-9d01-40b0-a4f0-22adf3490cbc'

def convertir_en_temps(chaine):
    '''Convertit en date la chaîne de caractères de l'API'''
    return datetime.strptime(chaine.replace('T', ''), '%Y%m%d%H%M%S')

def convertir_en_chaine(dt):
    '''Convertit un datetime en chaîne de caractères au format de l'API'''
    return datetime.strftime(dt, '%Y%m%dT%H%M%S')

choisy_le_roi = 'stop_area:SNCF:87545285'
notre_dame = 'stop_area:SNCF:87785436'
chatelet = "stop_area:SNCF:87758607"
nanterre = "stop_area:SNCF:87758029"

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

# Interface Streamlit
st.title("Calculateur d'itinéraire SNCF")

# Chargement et sélection des gares
uploaded_file = st.file_uploader("Choisissez un fichier CSV des gares", type="csv")
if uploaded_file is not None:
    df_gares = pd.read_csv(uploaded_file)
    gare_depart_nom = st.selectbox("Choisissez la gare de départ", df_gares['Nom'].unique())
    gare_arrivee_nom = st.selectbox("Choisissez la gare d'arrivée", df_gares['Nom'].unique())
    id_gare_depart = df_gares[df_gares['Nom'] == gare_depart_nom]['Identifiant'].iloc[0]
    id_gare_arrivee = df_gares[df_gares['Nom'] == gare_arrivee_nom]['Identifiant'].iloc[0]
    
    # Sélection de la date et l'heure
    date_depart = st.date_input("Date de départ", datetime.now())
    heure_depart = st.time_input('Heure de départ', datetime.now().time())
    datetime_depart = datetime.combine(date_depart, heure_depart)
    
    def voyage(id_depart, id_arrivee, datetime_depart):
        date_depart_chaine = convertir_en_chaine(datetime_depart)
        response = requests.get(
            f'https://api.sncf.com/v1/coverage/sncf/journeys?from={id_depart}&to={id_arrivee}&datetime={date_depart_chaine}',
            auth=(token_auth, '')
        ).json()
        return extraire_donnees_trajet(response)
    
    if st.button("Calculer l'itinéraire"):
        trajet_df = voyage(id_gare_depart, id_gare_arrivee, datetime_depart)
        if not trajet_df.empty:
            st.subheader(f"Trajet de {gare_depart_nom} à {gare_arrivee_nom}")
            st.dataframe(trajet_df)
        else:
            st.write("Aucun trajet trouvé pour les options sélectionnées.")
else:
    st.write("Veuillez téléverser un fichier CSV des gares.")
