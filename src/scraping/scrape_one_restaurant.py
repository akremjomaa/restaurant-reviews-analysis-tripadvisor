import requests
from bs4 import BeautifulSoup
import logging
import random
import time
from geopy.geocoders import Nominatim
import json
import re

# Configuration des en-têtes HTTP pour l'accès aux pages
HEADERS = {
    "User-Agent": random.choice([
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    ]),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

# Configuration du logger pour suivre les événements dans le processus de scraping
logging.basicConfig(
    level=logging.INFO,  # Niveau minimal de log (INFO pour une vue plus générale)
    format="%(asctime)s - %(levelname)s - %(message)s"  # Format des messages log
)
geolocator = Nominatim(user_agent="restaurant_locator")  # Utilisation de geopy pour la géolocalisation


def fetch_page(url, max_retries=5, base_delay=5, max_delay=60):
    """
    Récupère une page web avec gestion des erreurs HTTP et des pauses adaptatives.
    :param url: L'URL de la page à récupérer.
    :param max_retries: Le nombre maximal de tentatives en cas d'échec.
    :param base_delay: Le délai de base entre les tentatives en secondes.
    :param max_delay: Le délai maximum entre les tentatives en secondes.
    :return: L'objet BeautifulSoup contenant le HTML de la page si succès, sinon None.
    """
    for attempt in range(max_retries):
        try:
            logging.info(f"Tentative {attempt + 1}/{max_retries} pour accéder à {url}")
            response = requests.get(url, headers=HEADERS, timeout=10)

            if response.status_code == 200:
                logging.info("Page chargée avec succès.")
                return BeautifulSoup(response.text, 'lxml')  # Parse la page HTML

            elif response.status_code == 403:  # Si le serveur bloque la requête
                delay = min(base_delay * (2 ** attempt), max_delay) + random.uniform(0, 3)
                logging.warning(f"403 détecté. Pause de {delay:.2f} secondes avant nouvelle tentative.")
                time.sleep(delay)
            else:
                logging.error(f"Erreur HTTP {response.status_code}. Tentative {attempt + 1} échouée.")
                break  # Si erreur HTTP autre que 403, arrête le scraping

        except requests.exceptions.RequestException as e:
            logging.error(f"Erreur réseau : {e}. Tentative {attempt + 1} échouée.")
            time.sleep(base_delay)  # Attente avant de réessayer
    logging.critical(f"Échec après {max_retries} tentatives pour accéder à {url}")
    return None


def scrape_restaurants(soup, max_results=10):
    """
    Scrape les restaurants à partir de l'objet BeautifulSoup d'une page de TripAdvisor.
    :param soup: L'objet BeautifulSoup contenant le HTML de la page de restaurants.
    :param max_results: Nombre maximal de restaurants à scraper à partir de la page.
    :return: Une liste de dictionnaires contenant le nom et l'URL de chaque restaurant.
    """
    restaurants = []
    if not soup:
        logging.error("Le contenu HTML est vide. Aucun restaurant à extraire.")
        return restaurants  # Retourne une liste vide si aucune donnée n'est disponible

    for index in range(1, max_results + 1):  # Limite le nombre de restaurants récupérés
        try:
            card = soup.find("div", {"data-test": f"{index}_list_item"})
            if not card:
                continue  # Si le restaurant n'est pas trouvé, on passe au suivant

            name_tag = card.find("a", class_="BMQDV _F Gv wSSLS SwZTJ FGwzt ukgoS")
            raw_name = name_tag.text.strip()  # Récupère le nom du restaurant
            name = re.sub(r"^\d+\.\s*", "", raw_name)  # Supprime le numéro d'ordre au début du nom
            url_tag = card.find("a", href=True)
            url = f"https://www.tripadvisor.fr{url_tag['href']}" if url_tag else None  # Récupère l'URL du restaurant

            if name and url:
                restaurants.append({"name": name, "url": url})  # Ajoute le restaurant à la liste
        except Exception as e:
            logging.warning(f"Erreur lors du traitement du restaurant {index} : {e}")

    return restaurants


def get_coordinates(restaurant_name, location="Lyon"):
    """
    Récupère les coordonnées GPS d'un restaurant à partir de son nom.
    :param restaurant_name: Nom du restaurant à géolocaliser.
    :param location: Localisation par défaut (Lyon).
    :return: Un dictionnaire contenant la latitude et la longitude.
    """
    try:
        location = geolocator.geocode(restaurant_name, timeout=10)  # Recherche des coordonnées du restaurant
        if location:
            return {"latitude": location.latitude, "longitude": location.longitude}
        else:
            return {"latitude": None, "longitude": None}
    except Exception as e:
        logging.error(f"Erreur lors de la géolocalisation : {e}")
        return {"latitude": None, "longitude": None}


def save_restaurant_data(file_path="data/raw/list_restaurants_found.json"):
    """
    Récupère la liste des restaurants, scrape leurs informations et les sauvegarde dans un fichier JSON.
    :param file_path: Chemin du fichier de sauvegarde des données des restaurants.
    """
    base_url = "https://www.tripadvisor.fr/FindRestaurants?geo=187265"
    soup = fetch_page(base_url)  # Récupère la page principale de la liste des restaurants

    if not soup:
        print("Erreur : Impossible de charger la page principale.")
        return

    restaurants = scrape_restaurants(soup, max_results=10)  # Scrape la liste des restaurants
    if not restaurants:
        print("Erreur : Aucun restaurant trouvé.")
        return

    print(f"{len(restaurants)} restaurants trouvés. Récupération des coordonnées...")
    for restaurant in restaurants:
        coords = get_coordinates(restaurant["name"])  # Récupère les coordonnées de chaque restaurant
        restaurant["latitude"] = coords.get("latitude")
        restaurant["longitude"] = coords.get("longitude")

    # Sauvegarde des restaurants dans un fichier JSON
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(restaurants, f, ensure_ascii=False, indent=4)
    print(f"Données sauvegardées dans {file_path}.")
