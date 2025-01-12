import streamlit as st
import plotly.express as px
import pandas as pd


def map_interface(connection):
    query = """
    SELECT name, latitude, longitude
    FROM restaurants
    WHERE latitude IS NOT NULL AND longitude IS NOT NULL
    """
    restaurants = pd.read_sql_query(query, connection)

    st.markdown("## 🗺️ Carte Interactive des Restaurants")
    fig = px.scatter_mapbox(
        restaurants,
        lat="latitude",
        lon="longitude",
        hover_name="name",
        mapbox_style="carto-positron",
        title="Localisation des Restaurants"
    )
    st.plotly_chart(fig)
