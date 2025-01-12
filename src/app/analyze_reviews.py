import streamlit as st
import pandas as pd
import plotly.express as px


def analyze_reviews_interface(connection):
    query_restaurants = """
    SELECT id_restaurant, name
    FROM restaurants
    """
    restaurants = pd.read_sql_query(query_restaurants, connection)

    query_reviews = """
    SELECT id_restaurant, author, rating, review_date, review_text
    FROM reviews
    """
    reviews = pd.read_sql_query(query_reviews, connection)

    st.markdown("## 🔍 Analyse des Avis")
    selected_restaurant = st.selectbox("Choisissez un restaurant :", restaurants["name"])
    restaurant_id = restaurants[restaurants["name"] == selected_restaurant]["id_restaurant"].values[0]

    restaurant_reviews = reviews[reviews["id_restaurant"] == restaurant_id]

    st.markdown("### 📝 Avis")
    st.dataframe(restaurant_reviews)

    st.markdown("### 📊 Distribution des Notes")
    fig = px.histogram(
        restaurant_reviews,
        x="rating",
        nbins=10,
        title=f"Distribution des Notes pour {selected_restaurant}",
        labels={"rating": "Note"}
    )
    st.plotly_chart(fig)
