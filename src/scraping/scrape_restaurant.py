import requests
from bs4 import BeautifulSoup
import logging
import random
import time
from geopy.geocoders import Nominatim
import json
import re


# Configuration des en-têtes et logs
HEADERS = {
    "User-Agent": random.choice([
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    ]),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
geolocator = Nominatim(user_agent="restaurant_locator")


def fetch_page(url, max_retries=5, base_delay=5, max_delay=60):
    for attempt in range(max_retries):
        try:
            logging.info(f"Tentative {attempt + 1}/{max_retries} pour accéder à {url}")
            response = requests.get(url, headers=HEADERS, timeout=10)
            if response.status_code == 200:
                logging.info("Page chargée avec succès.")
                return BeautifulSoup(response.text, 'lxml')
            elif response.status_code == 403:
                delay = min(base_delay * (2 ** attempt), max_delay) + random.uniform(0, 3)
                logging.warning(f"403 détecté. Pause de {delay:.2f} secondes avant nouvelle tentative.")
                time.sleep(delay)
            else:
                logging.error(f"Erreur HTTP {response.status_code}. Tentative {attempt + 1} échouée.")
        except requests.exceptions.RequestException as e:
            logging.error(f"Erreur réseau : {e}. Tentative {attempt + 1} échouée.")
            time.sleep(base_delay)
    logging.critical(f"Échec après {max_retries} tentatives pour accéder à {url}")
    return None


def scrape_restaurants(soup, max_results=10):
    restaurants = []
    if not soup:
        logging.error("Le contenu HTML est vide. Aucun restaurant à extraire.")
        return restaurants

    for index in range(1, max_results + 1):
        try:
            card = soup.find("div", {"data-test": f"{index}_list_item"})
            if not card:
                continue
            name_tag = card.find("a", class_="BMQDV _F Gv wSSLS SwZTJ FGwzt ukgoS")
            raw_name = name_tag.text.strip()
            # Supprimer le numéro de position s'il existe (ex: "1. ")
            name = re.sub(r"^\d+\.\s*", "", raw_name)
            url_tag = card.find("a", href=True)
            url = f"https://www.tripadvisor.fr{url_tag['href']}" if url_tag else None

            if name and url:
                restaurants.append({"name": name, "url": url})
        except Exception as e:
            logging.warning(f"Erreur lors du traitement du restaurant {index} : {e}")

    return restaurants


def get_coordinates(restaurant_name, location="Lyon"):
    try:
        location = geolocator.geocode(restaurant_name, timeout=10)
        if location:
            return {"latitude": location.latitude, "longitude": location.longitude}
        else:
            return {"latitude": None, "longitude": None}
    except Exception as e:
        logging.error(f"Erreur lors de la géolocalisation : {e}")
        return {"latitude": None, "longitude": None}
    
def save_restaurant_data(file_path="restaurants_data.json"):
    """
    Scrape les restaurants et leurs coordonnées, puis les sauvegarde dans un fichier JSON.
    :param file_path: Chemin du fichier de sauvegarde.
    """
    base_url = "https://www.tripadvisor.fr/FindRestaurants?geo=187265"
    soup = fetch_page(base_url)

    if not soup:
        print("Erreur : Impossible de charger la page principale.")
        return

    restaurants = scrape_restaurants(soup, max_results=10)
    if not restaurants:
        print("Erreur : Aucun restaurant trouvé.")
        return

    print(f"{len(restaurants)} restaurants trouvés. Récupération des coordonnées...")
    for restaurant in restaurants:
        coords = get_coordinates(restaurant["name"])
        restaurant["latitude"] = coords.get("latitude")
        restaurant["longitude"] = coords.get("longitude")

    # Sauvegarde dans un fichier JSON
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(restaurants, f, ensure_ascii=False, indent=4)
    print(f"Données sauvegardées dans {file_path}.")