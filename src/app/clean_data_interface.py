import streamlit as st
import subprocess
import sys


def clean_data_interface(raw_filepath, processed_filepath):
    """
    Interface Streamlit pour le nettoyage des données des restaurants.
    :param raw_filepath: Chemin vers les données brutes.
    :param processed_filepath: Chemin vers les données nettoyées.
    """
    st.title("🛠️ Nettoyage des Données")
    st.markdown("### 📝 Suivi du Nettoyage")
    python_executable = sys.executable  # Identifie l'exécutable Python utilisé

    if st.button("Démarrer le Nettoyage des Données"):
        with st.spinner("⏳ Nettoyage en cours, veuillez patienter..."):
            try:
                # Lancer le script clean_data.py
                result = subprocess.run(
                    [python_executable, "src/processing/clean_data.py", raw_filepath, processed_filepath],
                    capture_output=True,
                    text=True,
                    check=True,
                )

                # Affichage des logs dans une zone déroulante
                st.success("🎉 Nettoyage terminé avec succès !")
            except subprocess.CalledProcessError as e:
                # Afficher les erreurs dans une zone déroulante
                st.error("❌ Une erreur est survenue lors du nettoyage des données.")
                with st.expander("🛠️ Détails de l'erreur"):
                    st.text(e.stderr)
