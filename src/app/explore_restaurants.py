import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, DataReturnMode
import plotly.express as px
import sqlite3


def explore_restaurants_interface(connection):
    """
    Interface Streamlit pour explorer les restaurants depuis la base de données SQLite.
    :param connection: Connexion active à la base de données SQLite.
    """
    try:
        # Vérifier si la table restaurants existe
        cursor = connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='restaurants';")
        if not cursor.fetchone():
            st.error("⚠️ La base de données est vide ou n'existe pas.")
            st.info("Veuillez d'abord créer et alimenter la base de données.")
            return

        # Charger les données des restaurants
        query_restaurants = """
        SELECT id_restaurant, name, street, postal_code, city, country, overall_rating, ranking,
               cuisine_rating, service_rating, qualite_prix_rating, ambiance_rating, price_range
        FROM restaurants
        """
        restaurants = pd.read_sql_query(query_restaurants, connection)

        # Charger le nombre réel d'avis par restaurant
        query_reviews_count = """
        SELECT id_restaurant, COUNT(*) AS real_reviews_count
        FROM reviews
        GROUP BY id_restaurant
        """
        reviews_count_data = pd.read_sql_query(query_reviews_count, connection)

        # Fusionner les données pour inclure le nombre réel d'avis
        restaurants = pd.merge(
            restaurants,
            reviews_count_data,
            on="id_restaurant",
            how="left"
        )
        restaurants["real_reviews_count"] = restaurants["real_reviews_count"].fillna(0).astype(int)

        # Vérifier si des données sont disponibles
        if restaurants.empty:
            st.warning("⚠️ Aucun restaurant disponible dans la base de données.")
            return

        # Charger les dates des avis
        query_review_dates = """
        SELECT MIN(review_date) AS min_date, MAX(review_date) AS max_date
        FROM reviews
        """
        review_dates = pd.read_sql_query(query_review_dates, connection)
        min_date = review_dates["min_date"].iloc[0]
        max_date = review_dates["max_date"].iloc[0]

        # Résumé des données
        num_restaurants = restaurants.shape[0]
        num_reviews = restaurants["real_reviews_count"].sum()
        avg_rating = restaurants["overall_rating"].mean()
        avg_reviews_per_restaurant = restaurants["real_reviews_count"].mean()

        st.markdown("## 🌟 Vue globale des Restaurants")

        st.markdown("### 📝 Résumé")
        st.write(f"- **Nombre total de restaurants disponibles** : {num_restaurants}")
        st.write(f"- **Nombre total d'avis enregistrés** : {num_reviews}")
        st.write(f"- **Note moyenne globale** : {avg_rating:.2f}")
        st.write(f"- **Nombre moyen d'avis par restaurant** : {avg_reviews_per_restaurant:.2f}")
        st.write(f"- **Période des avis** : de {min_date} à {max_date}")

        # Graphiques globaux
        st.markdown("### 📊 Graphiques Globaux")

        fig_rating_distribution = px.histogram(
            restaurants,
            x="overall_rating",
            nbins=10,
            title="Distribution des Notes des Restaurants",
            labels={"overall_rating": "Note Globale"},
            color_discrete_sequence=["#4C78A8"]
        )
        st.plotly_chart(fig_rating_distribution, use_container_width=True)

        fig_reviews_distribution = px.histogram(
            restaurants,
            x="real_reviews_count",
            nbins=15,
            title="Distribution du Nombre d'Avis par Restaurant",
            labels={"real_reviews_count": "Nombre d'Avis"},
            color_discrete_sequence=["#F58518"]
        )
        st.plotly_chart(fig_reviews_distribution, use_container_width=True)

        # Section des filtres
        st.markdown("### 🎛️ Filtres et Tableau")

        col1, col2, col3 = st.columns(3)

        with col1:
            min_rating = st.slider(
                "Note Minimale",
                min_value=0.0,
                max_value=5.0,
                value=0.0,
                step=0.5
            )

        with col2:
            min_reviews = st.slider(
                "Nombre Minimum d'Avis Réels",
                min_value=0,
                max_value=restaurants["real_reviews_count"].max(),
                value=0,
                step=5
            )

        with col3:
            postal_code_filter = st.multiselect(
                "Codes Postaux",
                options=sorted(restaurants["postal_code"].dropna().unique().tolist()),
                default=[]
            )

        # Application des filtres
        filtered_data = restaurants[
            (restaurants["overall_rating"] >= min_rating) &
            (restaurants["real_reviews_count"] >= min_reviews)
        ]
        if postal_code_filter:
            filtered_data = filtered_data[filtered_data["postal_code"].isin(postal_code_filter)]

        columns_to_display = [col for col in filtered_data.columns if col != "id_restaurant"]
        filtered_data_no_id = filtered_data[columns_to_display]

        # Tableau interactif avec AgGrid
        st.markdown("### 📊 Tableau des Restaurants")
        gb = GridOptionsBuilder.from_dataframe(filtered_data_no_id)
        gb.configure_pagination(paginationAutoPageSize=True)
        gb.configure_default_column(editable=False, groupable=True)

        sortable_columns = ["overall_rating", "real_reviews_count", "postal_code", "name"]
        for col in sortable_columns:
            gb.configure_column(col, sortable=True)

        grid_options = gb.build()

        grid_response = AgGrid(
            filtered_data_no_id,
            gridOptions=grid_options,
            data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
            update_mode="MODEL_CHANGED",
            height=500,
            theme="alpine"
        )

        # Téléchargement des données filtrées
        filtered_df = pd.DataFrame(grid_response["data"])
        st.markdown("### 📥 Télécharger les Données")
        csv_data = filtered_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Télécharger les Données Filtrées",
            data=csv_data,
            file_name="filtered_restaurants.csv",
            mime="text/csv"
        )

    except sqlite3.Error as e:
        st.error(f"Erreur lors de l'accès à la base de données : {e}")
