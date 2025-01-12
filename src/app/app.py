import streamlit as st
from explore_restaurants import explore_restaurants_interface
from analyze_reviews import analyze_reviews_interface
from map_interface import map_interface
from db_utils import get_db_connection

def main():
    st.set_page_config(page_title="Restaurants Lyonnais", layout="wide")
    st.sidebar.title("📊 Navigation")
    menu = st.sidebar.radio(
        "Choisissez une page",
        ["Explorer les Restaurants", "Analyse des Avis", "Carte Interactive"],
    )

    connection = get_db_connection()

    if menu == "Explorer les Restaurants":
        explore_restaurants_interface(connection)
    elif menu == "Analyse des Avis":
        analyze_reviews_interface(connection)
    elif menu == "Carte Interactive":
        map_interface(connection)

    connection.close()

if __name__ == "__main__":
    main()
