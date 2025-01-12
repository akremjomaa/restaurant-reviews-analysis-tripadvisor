import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, DataReturnMode


def explore_restaurants_interface(connection):
    """
    Interface Streamlit pour explorer les restaurants depuis la base de données SQLite.
    :param connection: Connexion active à la base de données SQLite.
    """
    # Récupération des données des restaurants
    query_restaurants = """
    SELECT *
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

    # Titre de la section
    st.markdown("## 🌟 Explorer les Restaurants")

    # Section des filtres
    st.markdown("### 🎛️ Filtres et Options")

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
