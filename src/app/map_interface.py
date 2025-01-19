import streamlit as st
import plotly.express as px
import pandas as pd
from mistralai import Mistral
import os 
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("MISTRAL_API_KEY")
model = "mistral-large-latest"
mistral_client = Mistral(api_key=api_key)

def map_interface(connection):
    # Sous-requête pour sélectionner les 5 avis les plus récents par restaurant
    query = """
    WITH recent_reviews AS (
        SELECT re.id_restaurant, re.review_text, re.review_date, re.rating,
               ROW_NUMBER() OVER (PARTITION BY re.id_restaurant ORDER BY re.review_date DESC) AS row_num
        FROM reviews re
    )
    SELECT r.name, r.street, r.latitude, r.longitude, AVG(rr.rating) AS average_rating, 
           GROUP_CONCAT(rr.review_text, ' ') AS all_reviews
    FROM restaurants r
    LEFT JOIN recent_reviews rr ON r.id_restaurant = rr.id_restaurant AND rr.row_num <= 5
    WHERE r.latitude IS NOT NULL AND r.longitude IS NOT NULL
    GROUP BY r.id_restaurant
    """
    
    restaurants = pd.read_sql_query(query, connection)

    # Résumer les avis pour chaque restaurant
    def summarize_reviews(reviews):
        if reviews:
            try:
                chat_response = mistral_client.chat.complete(
                    model=model,
                    messages=[
                        {
                            "role": "system",
                            "content": """
                            Tu es un assistant pour une application de recensement de restaurants. 
                            Ton rôle est de produire un résumé concis des derniers avis postés par les
                            clients du restaurant. 
                            Ne détaille pas chaque avis une par un, tu dois extraire ce qui
                            en ressort globalement.
                            Ne mentionne pas "les clients".
                            Essaye d'éviter les informations redondantes.
                            Ton résumé doit faire une trentaine de mots.
                            Ajoute une balise <br> tous les 4 à 7 mots, en fonction de la taille de ces derniers.
                            Plus les mots sont longs, moins les balises doivent être espacées.
                            Ajoute aussi des espaces quand nécessaire.
                            Ton objectif est de fournir un texte en format justifié.
                            """,
                        },
                        {
                            "role": "user",
                            "content": reviews,
                        },
                    ]
                )
                return chat_response.choices[0].message.content
            except Exception:
                return "Résumé indisponible."
        return "Aucun avis disponible."

    restaurants["review_summary"] = restaurants["all_reviews"].apply(summarize_reviews)

    st.markdown("## 🗺️ Carte Interactive des Restaurants")

    # Ajouter des informations au survol avec un style propre et largeur fixe
    restaurants["hover_info"] = (
        "<b>Nom:</b> " + restaurants["name"] +
        "<br><b>Adresse:</b> " + restaurants["street"] +
        "<br><b>Note Moyenne:</b> " + restaurants["average_rating"].round(1).astype(str) +
        "<br><b>Résumé:</b> " + restaurants["review_summary"]
    )

    # Modifier la taille de la carte
    fig = px.scatter_mapbox(
        restaurants,
        lat="latitude",
        lon="longitude",
        hover_name=None,  # Désactiver le nom simple
        hover_data=None,  # Supprimer les colonnes inutiles du survol
        mapbox_style="carto-positron",
        title="Localisation des Restaurants",
        width=900,  # Largeur de la carte
        height=700  # Hauteur de la carte
    )

    # Ajouter les informations d'infobulle
    fig.update_traces(marker=dict(size=10, color="blue"),
                      hovertemplate=restaurants["hover_info"])

    # Améliorer les styles de la carte
    fig.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},  # Supprimer les marges
        hoverlabel=dict(
            bgcolor="black",  # Fond noir pour l'infobulle
            font_size=12,
            font_family="Arial",
            font_color="white"  # Texte blanc dans l'infobulle
        ),
        mapbox=dict(
            zoom=13  # Réglez le niveau de zoom ici
        )
    )

    st.plotly_chart(fig, use_container_width=False)
