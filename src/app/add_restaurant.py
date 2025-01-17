import streamlit as st
from streamlit_folium import st_folium
import folium
import json
from processing.process_single_restaurant import process_and_add_restaurant
from scraping.scrape_restaurant import save_restaurant_data


def load_restaurant_data(file_path="restaurants_data.json"):
    """
    Charge les données des restaurants depuis un fichier JSON.
    :param file_path: Chemin du fichier JSON.
    :return: Liste des restaurants.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def display_map(restaurants):
    """
    Affiche une carte interactive avec les restaurants.
    """
    base_location = [45.75, 4.85]  # Coordonnées de Lyon
    m = folium.Map(location=base_location, zoom_start=13)

    for restaurant in restaurants:
        lat = restaurant.get("latitude")
        lon = restaurant.get("longitude")
        name = restaurant.get("name")
        url = restaurant.get("url")

        if lat and lon:
            popup_content = f"<b>{name}</b><br><a href='{url}' target='_blank'>Voir sur TripAdvisor</a>"
            folium.Marker(
                location=[lat, lon],
                popup=folium.Popup(popup_content, max_width=300),
                tooltip=name,
            ).add_to(m)

    return m


def add_restaurant_interface():
    """
    Interface principale pour ajouter des restaurants.
    """
    st.title("🗺️ Carte Interactive des Restaurants à Lyon")

    # Vérifier si les données existent déjà
    if "restaurants_data" not in st.session_state:
        st.session_state["restaurants_data"] = load_restaurant_data("restaurants_data.json")
        st.session_state["show_map"] = False  # État pour afficher ou non la carte

    # Bouton pour lancer le scraping
    if st.button("🔍 Lancer le scraping des restaurants"):
        with st.spinner("Récupération des données en cours, veuillez patienter..."):
            save_restaurant_data("restaurants_data.json")
            st.session_state["restaurants_data"] = load_restaurant_data("restaurants_data.json")
        st.success("Données récupérées et sauvegardées avec succès !")

    # Vérifier si des restaurants sont disponibles
    if not st.session_state["restaurants_data"]:
        st.warning("Aucune donnée disponible. Veuillez lancer le scraping.")
    else:
        # Bouton pour afficher la carte
        if st.button("🗺️ Afficher la carte des restaurants") or st.session_state.get("show_map", False):
            st.session_state["show_map"] = True
            st.success(f"{len(st.session_state['restaurants_data'])} restaurants trouvés.")
            map_ = display_map(st.session_state["restaurants_data"])
            map_data = st_folium(map_, width=700, height=500)

            # Vérifier si un popup a été cliqué
            if map_data and map_data.get("last_object_clicked"):
                clicked_name = map_data["last_object_clicked_tooltip"]
                clicked_restaurant = next(
                    (r for r in st.session_state["restaurants_data"] if r["name"] == clicked_name), None
                )
                if clicked_restaurant:
                    st.info(f"Restaurant sélectionné : {clicked_restaurant['name']}")

                    if st.button(f"Scraper et ajouter {clicked_restaurant['name']} à la base de données"):
                        process_and_add_restaurant(clicked_restaurant["url"])
                        st.success(f"{clicked_name} a été ajouté à la base de données avec succès !")

                else:
                    st.warning("Restaurant sélectionné introuvable dans les données disponibles.")
