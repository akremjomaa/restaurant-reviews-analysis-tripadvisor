import sqlite3
from geopy.geocoders import Nominatim
from geopy.exc import GeopyError
import logging
import time
from processing.clean_data import get_coordinates
from database.add_restaurant_to_db import add_restaurant_to_wr  
from typing import List, Dict


# Initialisation du géolocalisateur
geolocator = Nominatim(user_agent="restaurant_locator")

# Configuration du logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
     handlers=[
        logging.FileHandler("preprocessing.log", mode="a", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# def get_coordinates(address: str, name: str) -> dict:
#     """
#     Obtenir les coordonnées GPS d'une adresse. Si l'adresse échoue, tente avec le nom du restaurant.
#     :param address: Adresse complète.
#     :param name: Nom du restaurant.
#     :return: Dictionnaire contenant latitude et longitude.
#     """
#     retries = 3  # Nombre de tentatives
#     delay = 2  # Délai initial entre les tentatives

#     for attempt in range(retries):
#         try:
#             # Essayer avec l'adresse
#             location = geolocator.geocode(address, timeout=10)
#             if location:
#                 return {"latitude": location.latitude, "longitude": location.longitude}

#             # Si l'adresse échoue, tenter avec le nom du restaurant
#             logger.warning(f"Tentative {attempt + 1}/{retries} échouée avec l'adresse. Tentative avec le nom : {name}")
#             location = geolocator.geocode(name, timeout=10)
#             if location:
#                 return {"latitude": location.latitude, "longitude": location.longitude}

#         except GeopyError as e:
#             logger.error(f"Erreur lors de la géolocalisation (Tentative {attempt + 1}/{retries}) : {e}")
#             time.sleep(delay)
#             delay *= 2  # Double le délai entre les tentatives

#     # Si toutes les tentatives échouent
#     logger.error(f"Impossible d'obtenir les coordonnées pour : Adresse='{address}', Nom='{name}'")
#     return {"latitude": None, "longitude": None}

def convert_reviews(reviews: List[Dict]) -> List[Dict]:
    """
    Convertir les types des données des avis et standardiser les formats.
    :param reviews: Liste des avis bruts.
    :return: Liste des avis traités.
    """
    for review in reviews:
        try:
            review["contributions"] = int(review.get("contributions", 0))
            review["rating"] = float(review.get("rating", 0))

            # Gestion et formatage de la date de l'avis
            raw_date = review.get("review_date", "")
            review["review_date"] = (
                raw_date.replace("Rédigé le ", "").strip()
                if "Rédigé le" in raw_date
                else raw_date.strip()
            )
        except Exception as e:
            logger.error(f"Erreur lors du traitement d'un avis : {e}")
    return reviews

def preprocess_single_restaurant(restaurant: dict) -> dict:
    """
    Prétraite les données d'un seul restaurant.
    :param restaurant: Dictionnaire brut du restaurant.
    :return: Dictionnaire nettoyé et structuré.
    """
    logger.info(f"Prétraitement des données pour {restaurant.get('name', 'Nom inconnu')}.")

    def convert_price_range(price_range: str) -> str:
        try:
            return price_range.replace("\u202f", "").replace(",", ".").replace("€", "").strip()
        except Exception as e:
            logger.warning(f"Erreur lors de la conversion de la fourchette de prix : {e}")
            return price_range

    attribute_mapping = {
        "name": "name",
        "address": "address",
        "reviews_count": "reviews_count",
        "rating": "overall_rating",
        "ranking": "ranking",
        "total_restaurants": "total_restaurants",
        "Cuisine": "cuisine_rating",
        "Service": "service_rating",
        "Rapport qualité-prix": "qualite_prix_rating",
        "Ambiance": "ambiance_rating",
        "FOURCHETTE DE PRIX": "price_range",
        "CUISINES": "cuisines",
        "Régimes spéciaux": "special_diets",
        "Repas": "meals",
        "FONCTIONNALITÉS": "features",
        "reviews": "reviews"
    }

    processed_restaurant = {}
    for key, value in restaurant.items():
        try:
            new_key = attribute_mapping.get(key, key)
            if new_key == "price_range" and isinstance(value, str):
                processed_restaurant[new_key] = convert_price_range(value)
            elif new_key == "overall_rating" and isinstance(value, str):
                processed_restaurant[new_key] = float(value.replace(",", "."))
            elif new_key in ["cuisine_rating", "service_rating", "qualite_prix_rating", "ambiance_rating"]:
                processed_restaurant[new_key] = float(value) if value is not None else None
            elif new_key in ["reviews_count", "ranking", "total_restaurants"]:
                processed_restaurant[new_key] = int(value) if value is not None else None
            elif new_key == "reviews":
                processed_restaurant[new_key] = convert_reviews(value)  # Appel à la fonction
            else:
                processed_restaurant[new_key] = value
        except Exception as e:
            logger.warning(f"Erreur lors du traitement de la clé {key} avec la valeur {value} : {e}")

    return processed_restaurant


def split_address(restaurant: dict) -> dict:
    """
    Divise le champ 'address' en 'street', 'postal_code', 'city', et 'country'.
    :param restaurant: Dictionnaire du restaurant.
    :return: Dictionnaire mis à jour.
    """
    try:
        street, postal_city = restaurant['address'].split(',', 1)
        postal_code, city_country = postal_city.strip().split(' ', 1)
        city, country = city_country.rsplit(' ', 1)
        restaurant['street'] = street.strip()
        restaurant['postal_code'] = postal_code.strip()
        restaurant['city'] = city.strip()
        restaurant['country'] = country.strip()
        logger.info(f"Adresse divisée avec succès pour {restaurant.get('name', 'Nom inconnu')}.")
    except Exception as e:
        logger.error(f"Erreur lors de la division de l'adresse : {e}. Valeur de l'adresse : {restaurant.get('address', 'Non disponible')}")
        restaurant['street'] = restaurant.get('address', None)
        restaurant['postal_code'] = None
        restaurant['city'] = None
        restaurant['country'] = None

    restaurant.pop('address', None)
    return restaurant

def process_and_save_single_restaurant(restaurant: dict):
    """
    Traite un restaurant (nettoyage, géolocalisation, et ajout à la base de données).
    :param restaurant: Dictionnaire brut du restaurant.
    """
    logger.info(f"Traitement du restaurant : {restaurant.get('name', 'Nom inconnu')}")
    print(restaurant)

    try:
        # Étape 1 : Nettoyage des données
        cleaned_restaurant = preprocess_single_restaurant(restaurant)
        logger.info(f"Données nettoyées pour {cleaned_restaurant.get('name', 'Nom inconnu')}.")

        # Étape 2 : Ajout des coordonnées GPS
        coordinates = get_coordinates(
            cleaned_restaurant.get("address", ""),
            cleaned_restaurant.get("name", "")
        )
        cleaned_restaurant.update(coordinates)
        logger.info(f"Coordonnées ajoutées : {coordinates}")

        # Étape 3 : Division de l'adresse
        cleaned_restaurant = split_address(cleaned_restaurant)
        logger.info(f"Adresse divisée : {cleaned_restaurant.get('street', 'Adresse inconnue')}")

        # Retourner les données nettoyées
        return cleaned_restaurant

    except Exception as e:
        logger.error(f"Erreur lors du traitement du restaurant {restaurant.get('name', 'Nom inconnu')} : {e}", exc_info=True)
        return None


from scraping.scraper_utils import scrape_restaurant

def process_and_add_restaurant(restaurant_url, db_path="src/database/restaurants.db"):
    """
    Pipeline complet : scrape, nettoie et ajoute un restaurant à la base de données.
    :param restaurant_url: URL du restaurant à scraper.
    :param db_path: Chemin de la base de données SQLite.
    """
    # Étape 1 : Scraper les données du restaurant
    scraped_data = scrape_restaurant(restaurant_url)
    if not scraped_data:
        print("Erreur : Impossible de scraper les données du restaurant.")
        return

    # Étape 2 : Nettoyer les données du restaurant
    cleaned_data = process_and_save_single_restaurant(scraped_data)
    if not cleaned_data:
        print("Erreur : Nettoyage des données échoué.")
        return

    # Étape 3 : Ajouter les données nettoyées à la base de données
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    add_restaurant_to_wr(cursor, cleaned_data)

    conn.commit()
    conn.close()
    print(f"Le restaurant {cleaned_data['name']} a été ajouté à la base de données avec succès.")
