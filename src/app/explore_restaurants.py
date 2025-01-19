import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, DataReturnMode
import plotly.express as px
import sqlite3
import dateparser

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
      
        # Titre de l'application
        st.title("Analyse temporelle des notes des restaurants")
###Debut graphe 1
        # Chargement des données
        query = """
        SELECT 
            r.id_restaurant, 
            r.name AS restaurant_name, 
            rv.rating, 
            rv.review_date
        FROM reviews rv
        JOIN restaurants r ON r.id_restaurant = rv.id_restaurant;
        """
        data = pd.read_sql_query(query, connection)

        # Conversion des dates
        def convert_dates(date_str):
            if pd.isna(date_str):
                return None
            return dateparser.parse(date_str, languages=['fr'])

        data['review_date_converted'] = data['review_date'].apply(convert_dates)
        data['period'] = data['review_date_converted'].dt.to_period("1Y")  # Groupement par période de 1 an

        # Calcul des notes moyennes globales par période
        global_grouped = (
            data.groupby('period')['rating']
            .mean()
            .reset_index()
            .rename(columns={'rating': 'average_rating'})
        )
        global_grouped['period'] = global_grouped['period'].astype(str)
        global_grouped['period'] = pd.to_datetime(global_grouped['period'].str.split('-').str[0])

        # Affichage des données brutes globales (optionnel)
        #st.write("Données agrégées par période de 1 an (globales) :")
        #st.dataframe(global_grouped)

        # Option pour filtrer les données par restaurant
        restaurant_names = data['restaurant_name'].unique()
        selected_restaurant = st.selectbox("Sélectionnez un restaurant pour une analyse détaillée :", options=["Tous"] + list(restaurant_names))

        # Initialisation de la figure
        fig = px.line(
            global_grouped,
            x='period',
            y='average_rating',
            title="Évolution des notes moyennes des restaurants",
            labels={'period': 'Période', 'average_rating': 'Note Moyenne'},
            markers=True
        )

        # Ajout des données filtrées au graphique
        if selected_restaurant != "Tous":
            filtered_data = data[data['restaurant_name'] == selected_restaurant]
            filtered_grouped = (
                filtered_data.groupby('period')['rating']
                .mean()
                .reset_index()
                .rename(columns={'rating': 'average_rating'})
            )
            filtered_grouped['period'] = filtered_grouped['period'].astype(str)
            filtered_grouped['period'] = pd.to_datetime(filtered_grouped['period'].str.split('-').str[0])
            
            # Ajout de la courbe du restaurant spécifique
            fig.add_scatter(
                x=filtered_grouped['period'],
                y=filtered_grouped['average_rating'],
                mode='lines+markers',
                name=selected_restaurant
            )

        # Affichage du graphique
        st.plotly_chart(fig)

####Fin graphe 1

        # Option de sélection pour l'axe d'analyse
        analysis_axis = st.selectbox(
            "Sélectionnez l'axe d'analyse :",
            ["Type de Cuisine", "Régime Spécial", "Gamme de Prix"]
        )

        # Charger les données supplémentaires pour les caractéristiques des restaurants
        query_features = """
        SELECT 
            r.id_restaurant, r.overall_rating, c.name AS cuisine_name, d.name AS special_diet_name, r.price_range
        FROM restaurants r
        LEFT JOIN restaurant_cuisines rc ON r.id_restaurant = rc.id_restaurant
        LEFT JOIN cuisines c ON rc.id_cuisine = c.id_cuisine
        LEFT JOIN restaurant_special_diets rsd ON r.id_restaurant = rsd.id_restaurant
        LEFT JOIN special_diets d ON rsd.id_special_diet = d.id_special_diet
        """
        features = pd.read_sql_query(query_features, connection)

        # Préparation des données en fonction de l'axe d'analyse
        if analysis_axis == "Type de Cuisine":
            grouped_data = (
                features.groupby("cuisine_name")["overall_rating"]
                .mean()
                .reset_index()
                .rename(columns={"cuisine_name": "Catégorie", "overall_rating": "Note Moyenne"})
                .sort_values(by="Note Moyenne", ascending=False)
            )
            title = "Notes moyennes par type de cuisine"
            x_label = "Type de Cuisine"

        elif analysis_axis == "Régime Spécial":
            grouped_data = (
                features.groupby("special_diet_name")["overall_rating"]
                .mean()
                .reset_index()
                .rename(columns={"special_diet_name": "Catégorie", "overall_rating": "Note Moyenne"})
                .sort_values(by="Note Moyenne", ascending=False)
            )
            title = "Notes moyennes par régime spécial"
            x_label = "Régime Spécial"

        elif analysis_axis == "Gamme de Prix":
            grouped_data = (
                features.groupby("price_range")["overall_rating"]
                .mean()
                .reset_index()
                .rename(columns={"price_range": "Catégorie", "overall_rating": "Note Moyenne"})
                .sort_values(by="Note Moyenne", ascending=False)
            )
            title = "Notes moyennes par gamme de prix"
            x_label = "Gamme de Prix"

        # Création du graphique interactif
        fig = px.bar(
            grouped_data,
            x="Catégorie",
            y="Note Moyenne",
            title=title,
            labels={"Catégorie": x_label, "Note Moyenne": "Note Moyenne"},
            text="Note Moyenne"
        )

        st.plotly_chart(fig)
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
            file_name="data/processed/filtered_restaurants.csv",
            mime="text/csv"
        )
    except sqlite3.Error as e:
        st.error(f"Erreur lors de l'accès à la base de données : {e}")