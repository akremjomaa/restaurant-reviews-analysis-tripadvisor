from pathlib import Path
import json
import time
import random
from scraping.scraper_utils import scrape_restaurant_list, scrape_restaurant

def save_urls_to_json(urls, filename):
    """
    Sauvegarde les URLs des restaurants dans un fichier JSON.
    :param urls: Liste des URLs à sauvegarder.
    :param filename: Nom du fichier où sauvegarder les URLs.
    """
    # Définit le chemin du fichier à partir de la racine du projet
    base_dir = Path(__file__).resolve().parent.parent.parent  # Remonte à la racine
    filepath = base_dir / filename
    
    # Crée les dossiers si inexistants
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    # Sauvegarde la liste des URLs dans le fichier JSON
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(urls, f, ensure_ascii=False, indent=4)
    
    print(f"URLs sauvegardées dans {filepath}")

def save_to_json(data, filename):
    """
    Sauvegarde les données dans un fichier JSON.
    :param data: Les données à sauvegarder.
    :param filename: Le nom du fichier.
    """
    # Définit le chemin du fichier à partir de la racine du projet
    base_dir = Path(__file__).resolve().parent.parent.parent  # Remonte à la racine
    filepath = base_dir / filename
    
    # Crée les dossiers si inexistants
    filepath.parent.mkdir(parents=True, exist_ok=True)

    # Sauvegarde les données dans le fichier JSON
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
    print(f"Données sauvegardées dans {filepath}")


def main():
    """
    Fonction principale du script de scraping qui récupère la liste des restaurants et leurs détails,
    puis les sauvegarde dans des fichiers JSON.
    """
    # URL de la première page des restaurants à scraper
    base_url = "https://www.tripadvisor.fr/Restaurants-g187265-oa0-Lyon_Rhone_Auvergne_Rhone_Alpes.html"

    # Chemins des fichiers de sauvegarde des URLs et des données des restaurants
    urls_file = "data/raw/top_restaurants_urls.json"
    data_file = "data/raw/top_restaurants.json"

    # Scraping des URLs des restaurants
    print("Début du scraping des URLs des restaurants...")
    restaurant_urls = scrape_restaurant_list(base_url)

    # Scraping des informations détaillées de chaque restaurant
    print("Début du scraping des informations des restaurants...")
    all_restaurants_data = []
    
    for i, restaurant_url in enumerate(restaurant_urls):
        print(f"Scraping restaurant {i + 1}/{len(restaurant_urls)}: {restaurant_url}")
        
        # Scraping des données du restaurant à partir de son URL
        data = scrape_restaurant(restaurant_url)
        
        # Si des données ont été récupérées, on les ajoute à la liste
        if data:
            all_restaurants_data.append(data)
        
        # Pause pour éviter d'être bloqué par le serveur
        time.sleep(random.uniform(3, 7)) 

    # Sauvegarde des données des restaurants dans un fichier JSON
    if (save_to_json(all_restaurants_data, data_file)):
        save_urls_to_json(restaurant_urls, urls_file)

if __name__ == "__main__":
    # Exécute la fonction principale si ce script est appelé directement
    main()
