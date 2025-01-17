import os
import sqlite3
import streamlit as st
import subprocess


def database_exists(db_path="restaurants.db"):
    """
    Vérifie si la base de données SQLite existe et contient des tables.
    :param db_path: Chemin vers le fichier SQLite.
    :return: True si la base de données existe et contient des tables, sinon False.
    """
    if not os.path.exists(db_path):
        return False
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' LIMIT 1;")
        exists = cursor.fetchone() is not None
        conn.close()
        return exists
    except sqlite3.Error:
        return False


def run_create_warehouse():
    """
    Interface pour exécuter le script de création de l'entrepôt de données.
    """
    st.header("🏗️ Créer l'Entrepôt de Données")

    db_path = "restaurants.db"

    if database_exists(db_path):
        st.warning("⚠️ L'entrepôt de données existe déjà. Voulez-vous le recréer ?")
        if st.button("Recréer la base de données"):
            try:
                result = subprocess.run(
                    ["python", "src/database/create_warehouse.py"],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                st.success("Base de données recréée et alimentée avec succès !")
                st.text(result.stdout)
            except subprocess.CalledProcessError as e:
                st.error("Erreur lors de l'exécution du script de création de la base de données.")
                st.text(e.stderr)
    else:
        if st.button("Créer la base de données"):
            try:
                result = subprocess.run(
                    ["python", "src/database/create_warehouse.py"],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                st.success("Base de données créée et alimentée avec succès !")
                st.text(result.stdout)
            except subprocess.CalledProcessError as e:
                st.error("Erreur lors de l'exécution du script de création de la base de données.")
                st.text(e.stderr)
