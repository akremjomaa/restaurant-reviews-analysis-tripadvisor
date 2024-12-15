from pathlib import Path
import json
import time
import random
from utils import scrape_restaurant_list, scrape_restaurant

def save_urls_to_json(urls, filename):
    """
    Sauvegarde les URLs des restaurants dans un fichier JSON.
    :param urls: Liste des URLs à sauvegarder.
    :param filename: Nom du fichier où sauvegarder les URLs.
    """
    
    base_dir = Path(__file__).resolve().parent.parent.parent  # Remonte à la racine
    filepath = base_dir / filename
     # Crée les dossiers si inexistants
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(urls, f, ensure_ascii=False, indent=4)
    print(f"URLs sauvegardées dans {filepath}")

def save_to_json(data, filename):
    """
    Sauvegarde les données dans un fichier JSON.
    :param data: Les données à sauvegarder.
    :param filename: Le nom du fichier.
    """
    base_dir = Path(__file__).resolve().parent.parent.parent  # Remonte à la racine
    filepath = base_dir / filename
    # Crée les dossiers si inexistants
    filepath.parent.mkdir(parents=True, exist_ok=True)

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Données sauvegardées dans {filepath}")


def main():

# URL de la liste des restaurants
    base_url = "https://www.tripadvisor.fr/Restaurants-g187265-oa0-Lyon_Rhone_Auvergne_Rhone_Alpes.html"

      # Chemins des fichiers de sauvegarde
    urls_file = "data/raw/restaurant_urls_v3.json"
    data_file = "data/raw/top_15_restaurants_v3.json"

    # Scraper les URLs des restaurants
    print("Début du scraping des URLs des restaurants...")
    restaurant_urls = scrape_restaurant_list(base_url)
    save_urls_to_json(restaurant_urls,urls_file)  # Sauvegarde des URLs

    # Scraper les détails des restaurants
    print("Début du scraping des informations des restaurants...")
    all_restaurants_data = []
    for i, restaurant_url in enumerate(restaurant_urls):
        print(f"Scraping restaurant {i + 1}/{len(restaurant_urls)}: {restaurant_url}")
        data = scrape_restaurant(restaurant_url)
        if data:
            all_restaurants_data.append(data)
        time.sleep(random.uniform(3, 7)) 

    # Sauvegarde des données
    save_to_json(all_restaurants_data, data_file)

if __name__ == "__main__":
    main()