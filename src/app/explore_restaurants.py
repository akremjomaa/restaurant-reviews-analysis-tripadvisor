import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, DataReturnMode
import plotly.express as px

def explore_restaurants_interface(connection):
    """
    Interface Streamlit pour explorer les restaurants depuis la base de données SQLite.
    :param connection: Connexion active à la base de données SQLite.
    """
    # Récupération des données des restaurants
    query_restaurants = """
    SELECT id_restaurant, name, street, postal_code, city, country, overall_rating, ranking , cuisine_rating, service_rating, qualite_prix_rating, ambiance_rating, price_range
    FROM restaurants
    """
    restaurants = pd.read_sql_query(query_restaurants, connection)

    # Récupération du nombre réel d'avis pour chaque restaurant
    query_reviews_count = """
    SELECT id_restaurant, COUNT(*) AS real_reviews_count
    FROM reviews
    GROUP BY id_restaurant
    """
    reviews_count_data = pd.read_sql_query(query_reviews_count, connection)

    # Fusionner les données pour ajouter le vrai nombre d'avis
    restaurants = pd.merge(
        restaurants,
        reviews_count_data,
        on="id_restaurant",
        how="left"
    )
    restaurants["real_reviews_count"] = restaurants["real_reviews_count"].fillna(0).astype(int)

    # Récupération des dates des avis
    query_review_dates = """
    SELECT MIN(review_date) AS min_date, MAX(review_date) AS max_date
    FROM reviews
    """
    review_dates = pd.read_sql_query(query_review_dates, connection)
    min_date = review_dates["min_date"].iloc[0]
    max_date = review_dates["max_date"].iloc[0]

    # Récupérer les cuisines disponibles
    query_cuisines = """
    SELECT DISTINCT name FROM cuisines
    """
    cuisines = pd.read_sql_query(query_cuisines, connection)["name"].tolist()

    # Calculer des statistiques pour le résumé
    num_restaurants = restaurants.shape[0]
    num_reviews = restaurants["real_reviews_count"].sum()
    avg_rating = restaurants["overall_rating"].mean()
    avg_reviews_per_restaurant = restaurants["real_reviews_count"].mean()

    # Résumé des informations
    st.markdown("## 🌟 Vue globale des Restaurants")

    st.markdown("### 📝 Résumé")
    st.write(f"- **Nombre total de restaurants disponibles** : {num_restaurants}")
    st.write(f"- **Nombre total d'avis enregistrés** : {num_reviews}")
    st.write(f"- **Note moyenne globale** : {avg_rating:.2f}")
    st.write(f"- **Nombre moyen d'avis par restaurant** : {avg_reviews_per_restaurant:.2f}")
    st.write(f"- **Période des avis** : de {min_date} à {max_date}")

     # Graphiques globaux
    st.markdown("### 📊 Graphiques Globaux")

    # Distribution des notes
    fig_rating_distribution = px.histogram(
        restaurants,
        x="overall_rating",
        nbins=10,
        title="Distribution des Notes des Restaurants",
        labels={"overall_rating": "Note Globale"},
        color_discrete_sequence=["#4C78A8"]
    )
    st.plotly_chart(fig_rating_distribution, use_container_width=True)

    # Distribution des avis
    fig_reviews_distribution = px.histogram(
        restaurants,
        x="real_reviews_count",
        nbins=15,
        title="Distribution du Nombre d'Avis par Restaurant",
        labels={"real_reviews_count": "Nombre d'Avis"},
        color_discrete_sequence=["#F58518"]
    )
    st.plotly_chart(fig_reviews_distribution, use_container_width=True)

    # Top 10 des restaurants avec le plus d'avis
    top_10_reviews = restaurants.nlargest(10, "real_reviews_count")
    fig_top_10_reviews = px.bar(
        top_10_reviews,
        x="name",
        y="real_reviews_count",
        title="Top 10 des Restaurants par Nombre d'Avis",
        labels={"name": "Restaurant", "real_reviews_count": "Nombre d'Avis"},
        color="real_reviews_count",
        color_continuous_scale="Viridis"
    )
    fig_top_10_reviews.update_xaxes(tickangle=45)
    st.plotly_chart(fig_top_10_reviews, use_container_width=True)
    # Section des filtres
    st.markdown("### 🎛️ Filtres et Tableau")

    col1, col2, col3 = st.columns(3)

    # Filtre par note minimale
    with col1:
        min_rating = st.slider(
            "Note Minimale",
            min_value=0.0,
            max_value=5.0,
            value=0.0,
            step=0.5
        )

    # Filtre par nombre minimum d'avis
    with col2:
        min_reviews = st.slider(
            "Nombre Minimum d'Avis Réels",
            min_value=0,
            max_value=restaurants["real_reviews_count"].max(),
            value=0,
            step=5
        )

    # Filtre par codes postaux
    with col3:
        postal_code_filter = st.multiselect(
            "Codes Postaux",
            options=sorted(restaurants["postal_code"].dropna().unique().tolist()),
            default=[],
        )

    # Application des filtres
    filtered_data = restaurants[
        (restaurants["overall_rating"] >= min_rating) &
        (restaurants["real_reviews_count"] >= min_reviews)
    ]
    if postal_code_filter:
        filtered_data = filtered_data[filtered_data["postal_code"].isin(postal_code_filter)]

    # Exclure la colonne 'id_restaurant' de l'affichage
    columns_to_display = [col for col in filtered_data.columns if col != "id_restaurant"]
    filtered_data_no_id = filtered_data[columns_to_display]

    # Tableau interactif avec AgGrid
    st.markdown("### 📊 Tableau des Restaurants")
    gb = GridOptionsBuilder.from_dataframe(filtered_data_no_id)
    gb.configure_pagination(paginationAutoPageSize=True)  # Pagination automatique
    gb.configure_default_column(editable=False, groupable=True)  # Colonnes non modifiables

    # Activer le tri pour certaines colonnes
    sortable_columns = ["overall_rating", "real_reviews_count", "postal_code", "name"]
    for col in sortable_columns:
        gb.configure_column(col, sortable=True)

    # Options du tableau
    grid_options = gb.build()

    # Rendu du tableau avec AgGrid
    grid_response = AgGrid(
        filtered_data_no_id,
        gridOptions=grid_options,
        data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
        update_mode="MODEL_CHANGED",
        height=500,
        theme="alpine",  # Thème moderne et élégant
    )

    # Télécharger les données filtrées
    filtered_df = pd.DataFrame(grid_response["data"])
    st.markdown("### 📥 Télécharger les Données")
    csv_data = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Télécharger les Données Filtrées",
        data=csv_data,
        file_name="filtered_restaurants.csv",
        mime="text/csv"
    )