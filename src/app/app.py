import streamlit as st
import subprocess
import sys
from add_restaurant_interface import add_restaurant_interface
from map_interface import map_interface
from analyze_reviews import analyze_reviews_interface
from explore_restaurants import explore_restaurants_interface
from utils import get_db_connection


def execute_task(script_path, description):
    """
    Exécute un script Python et affiche les logs en temps réel.
    """
    st.info(f"⏳ {description} en cours...")
    python_executable = sys.executable
    with st.spinner(f"Exécution de {description}..."):
        process = subprocess.Popen(
            [python_executable, script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        logs_area = st.empty()
        for line in iter(process.stdout.readline, ""):
            logs_area.write(line.strip())
        process.stdout.close()
        process.wait()
    if process.returncode == 0:
        st.success(f"✅ {description} terminé avec succès !")
    else:
        st.error(f"❌ {description} a échoué.")


def scraping_section():
    """Section pour le scraping."""
    st.subheader("🔍 Étape 1 : Scraping des Données")
    st.write(
        """
        Cette étape consiste à extraire les informations des restaurants lyonnais et les avis des clients directement depuis TripAdvisor.
        """
    )
    if st.button("📥 Démarrer le Scraping"):
        execute_task("src/scraping/scraper.py", "Scraping des Données")


def cleaning_section():
    """Section pour le nettoyage."""
    st.subheader("🛠️ Étape 2 : Nettoyage des Données")
    st.write(
        """
        Nettoyez les données brutes extraites pour les structurer et les préparer pour l'analyse.
        """
    )
    if st.button("🧹 Démarrer le Nettoyage"):
        execute_task("src/processing/clean_data.py", "Nettoyage des Données")


def warehouse_section():
    """Section pour la création de l'entrepôt."""
    st.subheader("🏗️ Étape 3 : Création de l'Entrepôt de Données")
    st.write(
        """
        Créez une base de données optimisée pour stocker vos données nettoyées, prêtes pour l'analyse.
        """
    )
    if st.button("🏗️ Créer l'Entrepôt de Données"):
        execute_task("src/database/create_warehouse.py", "Création de l'Entrepôt de Données")


def navbar_vertical():
    """Navbar verticale à gauche pour la navigation."""
    with st.sidebar:
        st.image("data/tripadvisor.png", width=100)
        st.title("🍴 L'Observatoire des Saveurs Lyonnaises")
        st.markdown("---")
        menu = st.radio(
            "Menu",
            ["Accueil", "Explorer les Restaurants", "Analyse des Avis", "Carte Interactive", "Ajouter un restaurant"],
            index=0,
        )
        st.markdown("---")
        st.caption("Développé pour analyser les restaurants lyonnais.")
    return menu


def main():
    """Interface principale."""
    st.set_page_config(
        page_title="L'Observatoire des Saveurs Lyonnaises",
        layout="wide",
        page_icon="🍴",
    )

    menu = navbar_vertical()  # Charger la navbar

    connection = None
    if menu in ["Explorer les Restaurants", "Analyse des Avis", "Carte Interactive"]:
        try:
            connection = get_db_connection()
        except Exception:
            st.error("Erreur de connexion à la base de données.")
            st.stop()

    if menu == "Accueil":
        st.title("🍴 L'Observatoire des Saveurs Lyonnaises")
        st.markdown(
            """
            Bienvenue dans **L'Observatoire des Saveurs Lyonnaises** !
            
            Nous combinons web scraping, nettoyage de données et analyses interactives pour comprendre les avis des restaurants lyonnais.
            """
        )
        st.markdown("---")
        col1, col2, col3 = st.columns([0.5, 4, 1])
        with col2:
            scraping_section()
            st.markdown("<br>", unsafe_allow_html=True)  
            cleaning_section()
            st.markdown("<br>", unsafe_allow_html=True) 
            warehouse_section()

    elif menu == "Explorer les Restaurants":
        explore_restaurants_interface(connection)

    elif menu == "Analyse des Avis":
        analyze_reviews_interface(connection)

    elif menu == "Carte Interactive":
        map_interface(connection)

    elif menu == "Ajouter un restaurant":
        add_restaurant_interface()

    if connection:
        connection.close()


if __name__ == "__main__":
    main()
