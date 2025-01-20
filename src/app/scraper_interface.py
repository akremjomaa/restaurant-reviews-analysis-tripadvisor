import streamlit as st
import subprocess
import sys
from pathlib import Path

def check_existing_data():
    """
    Vérifie si les fichiers de données existent déjà.
    """
    urls_file = Path("data/raw/top_restaurants_urls.json")
    data_file = Path("data/raw/top_restaurants.json")
    return urls_file.exists(), data_file.exists()

def run_scraper():
    """
    Interface Streamlit pour exécuter le script de scraping et afficher les logs dans une zone dédiée.
    """
    st.title("🔍 Scraping des Restaurants")
    st.markdown("### 🕵️ Suivi des Étapes de Scraping")

    urls_file_exists, data_file_exists = check_existing_data()

    if urls_file_exists and data_file_exists:
        st.warning("Les fichiers de données existent déjà.")
        if not st.checkbox("Souhaitez-vous relancer le scraping ?", value=False):
            st.success("Le scraping n'a pas été relancé. Vous pouvez explorer les données existantes.")
            return

    if st.button("Démarrer le Scraping"):
        st.info("Le scraping a commencé, veuillez patienter...")

        python_executable = sys.executable
        process = subprocess.Popen(
            [python_executable, "src/scraping/scraper.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        stdout, stderr = process.communicate()

        st.markdown("### 📜 Logs du Scraping")
        log_area = st.empty()
        logs = stdout.strip().split("\n") if stdout else ["Aucun log disponible."]
        for log in logs:
            log_area.text(log)

        if process.returncode == 0:
            st.success("🎉 Scraping terminé avec succès !")
        else:
            st.error("❌ Une erreur est survenue pendant le scraping.")
            error_logs = stderr.strip().split("\n") if stderr else ["Aucune erreur spécifique."]
            st.markdown("### ⚠️ Logs des Erreurs")
            st.error("\n".join(error_logs))
