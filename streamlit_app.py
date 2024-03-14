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

def voyage(heure_depart):
    date_depart = convertir_en_chaine(heure_depart)

    # Choisy-le-Roi à Notre-Dame
    rer_c_ntr_dame_response = requests.get(
        f'https://api.sncf.com/v1/coverage/sncf/journeys?from={choisy_le_roi}&to={notre_dame}&datetime={date_depart}',
        auth=(token_auth, '')
    ).json()
    rer_c_df = extraire_donnees_trajet(rer_c_ntr_dame_response)
    derniere_arrivee_c = rer_c_df['Arrivee'].max()

    # Notre-Dame à Châtelet, départ basé sur l'arrivée de RER C
    date_depart = convertir_en_chaine(derniere_arrivee_c)
    rer_b_chatelet_response = requests.get(
        f'https://api.sncf.com/v1/coverage/sncf/journeys?from={notre_dame}&to={chatelet}&datetime={date_depart}',
        auth=(token_auth, '')
    ).json()
    rer_b_df = extraire_donnees_trajet(rer_b_chatelet_response)
    derniere_arrivee_b = rer_b_df['Arrivee'].max()

    # Châtelet à Nanterre, départ basé sur l'arrivée de RER B
    date_depart = convertir_en_chaine(derniere_arrivee_b)
    rer_a_nanterre_response = requests.get(
        f'https://api.sncf.com/v1/coverage/sncf/journeys?from={chatelet}&to={nanterre}&datetime={date_depart}',
        auth=(token_auth, '')
    ).json()
    rer_a_df = extraire_donnees_trajet(rer_a_nanterre_response)

    return rer_c_df, rer_b_df, rer_a_df

# Interface Streamlit
st.title("Calculateur d'itinéraire SNCF")

# Widgets pour sélectionner la date et l'heure de départ
date_depart = st.date_input("Date de départ", datetime.now())
heure_depart = st.time_input('Heure de départ', datetime.now().time())

datetime_depart = datetime.combine(date_depart, heure_depart)

if st.button("Calculer l'itinéraire"):
    rer_c, rer_b, rer_a = voyage(datetime_depart)

    st.subheader("Trajet de Choisy-le-Roi à Notre-Dame")
    st.dataframe(rer_c)

    st.subheader("Trajet de Notre-Dame à Châtelet")
    st.dataframe(rer_b)

    st.subheader("Trajet de Châtelet à Nanterre")
    st.dataframe(rer_a)
