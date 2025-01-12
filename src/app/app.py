import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

DB_PATH = "db/restaurants.db"

def connect_to_db():
    return sqlite3.connect(DB_PATH)

def load_data():
    conn = connect_to_db()
    restaurants = pd.read_sql_query("SELECT * FROM dim_restaurants", conn)
    reviews = pd.read_sql_query("SELECT * FROM fact_reviews", conn)
    conn.close()
    return restaurants, reviews

def homepage():
    st.markdown(
        """
        <div style="background-color:#4A90E2;padding:15px;border-radius:10px;">
            <h1 style="color:white;text-align:center;">Analyse des Avis des Restaurants</h1>
            <p style="color:white;text-align:center;">
                Découvrez, explorez et analysez les avis des clients sur les restaurants de Lyon.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

def explore_restaurants(restaurants):
    st.markdown("## 🌟 Explorer les Restaurants")
    selected_restaurant = st.selectbox("Choisissez un restaurant :", restaurants["name"])
    restaurant_data = restaurants[restaurants["name"] == selected_restaurant]
    st.write(restaurant_data.T)

def analyze_reviews(restaurants, reviews):
    st.markdown("## 🔍 Analyse des Avis")
    selected_restaurant = st.selectbox("Choisissez un restaurant :", restaurants["name"])
    restaurant_id = restaurants[restaurants["name"] == selected_restaurant]["restaurant_id"].values[0]
    restaurant_reviews = reviews[reviews["restaurant_id"] == restaurant_id]
    st.write("### Avis")
    st.write(restaurant_reviews)

def show_map(restaurants):
    st.markdown("## 🗺️ Carte Interactive")
    map_data = restaurants[["latitude", "longitude", "name"]].dropna()
    fig = px.scatter_mapbox(map_data, lat="latitude", lon="longitude", hover_name="name", mapbox_style="carto-positron")
    st.plotly_chart(fig)
# Ajouter un nouveau restaurant dans la base de données
def add_restaurant_to_db(name, address, rating, cuisine, latitude, longitude):
    conn = connect_to_db()
    try:
        query = """
        INSERT INTO dim_restaurants (name, address, overall_rating, cuisines, latitude, longitude)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        conn.execute(query, (name, address, rating, cuisine, latitude, longitude))
        conn.commit()
        st.success("Le restaurant a été ajouté avec succès !")
    except Exception as e:
        st.error(f"Erreur lors de l'ajout du restaurant : {e}")
    finally:
        conn.close()

# Interface pour ajouter un restaurant
def add_restaurant():
    st.markdown("## ➕ Ajouter un Nouveau Restaurant")
    with st.form("add_restaurant_form"):
        name = st.text_input("Nom du Restaurant")
        address = st.text_input("Adresse")
        rating = st.slider("Note Globale", 0.0, 5.0, step=0.1)
        cuisine = st.text_input("Type de Cuisine")
        latitude = st.text_input("Latitude (optionnel)")
        longitude = st.text_input("Longitude (optionnel)")

        submitted = st.form_submit_button("Ajouter")

        if submitted:
            if not name or not address:
                st.error("Veuillez remplir les champs obligatoires.")
            else:
                try:
                    latitude = float(latitude) if latitude else None
                    longitude = float(longitude) if longitude else None
                    add_restaurant_to_db(name, address, rating, cuisine, latitude, longitude)
                except ValueError:
                    st.error("Latitude et Longitude doivent être des nombres.")

def main():
    st.sidebar.title("📊 Navigation")
    menu = st.sidebar.radio(
        "Choisissez une page",
        ["Accueil", "Explorer les restaurants", "Analyse des avis", "Carte interactive", "Ajouter un restaurant"],
    )

    restaurants, reviews = load_data()

    if menu == "Accueil":
        homepage()
    elif menu == "Explorer les restaurants":
        explore_restaurants(restaurants)
    elif menu == "Analyse des avis":
        analyze_reviews(restaurants, reviews)
    elif menu == "Carte interactive":
        show_map(restaurants)
    elif menu == "Ajouter un restaurant":
        add_restaurant()

if __name__ == "__main__":
    main()
