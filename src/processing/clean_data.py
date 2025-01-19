import json
from typing import List, Dict
from geopy.geocoders import Nominatim
from geopy.exc import GeopyError
import time

# Initialisation du géolocalisateur
geolocator = Nominatim(user_agent="restaurant_locator")

def get_coordinates(address: str, name: str) -> Dict[str, float]:
    """
    Obtenir les coordonnées GPS d'une adresse. Si l'adresse échoue, tente avec le nom du restaurant.
    :param address: Adresse complète.
    :param name: Nom du restaurant.
    :return: Dictionnaire contenant latitude et longitude.
    """
    retries = 3  # Nombre de tentatives
    delay = 2  # Délai initial entre les tentatives

    for attempt in range(retries):
        try:
            # Essayer avec l'adresse
            location = geolocator.geocode(address, timeout=10)
            if location:
                return {"latitude": location.latitude, "longitude": location.longitude}

            # Si l'adresse échoue, tenter avec le nom du restaurant
            print(f"Échec de récupération des coordonnées du restaurant à partir de l'adresse. Nouvelle tentative en utilisant le nom du restaurant : {name}")
            location = geolocator.geocode(name, timeout=10)
            if location:
                return {"latitude": location.latitude, "longitude": location.longitude}

        except GeopyError as e:
            print(f"Tentative {attempt + 1}/{retries} échouée : {e}")
            time.sleep(delay)
            delay *= 2  # Double le délai entre les tentatives

    # Si toutes les tentatives échouent
    print(f"Échec pour l'adresse : {address} et le nom : {name}. Aucune coordonnée trouvée.")
    return {"latitude": None, "longitude": None}

def preprocess_restaurant_data(data: List[Dict]) -> List[Dict]:
    """
    Prétraiter les données des restaurants pour ajuster les noms des attributs et les types.
    :param data: Liste des dictionnaires représentant les données des restaurants.
    :return: Liste des dictionnaires avec les attributs et types normalisés.
    """
    def convert_price_range(price_range: str) -> str:
        """
        Convertir une fourchette de prix en une chaîne normalisée.
        :param price_range: Chaîne brute de la fourchette de prix.
        :return: Chaîne de prix normalisée.
        """
        try:
            return price_range.replace("\u202f", "").replace(",", ".").replace("€", "").strip()
        except Exception:
            return price_range

    def convert_reviews(reviews: List[Dict]) -> List[Dict]:
        """
        Convertir les types des données des avis et standardiser les formats.
        :param reviews: Liste des avis bruts.
        :return: Liste des avis traités.
        """
        for review in reviews:
            review["contributions"] = int(review.get("contributions", 0))
            review["rating"] = float(review.get("rating", 0))
            review["review_date"] = review.get("review_date", "").replace("Rédigé le ", "").strip()
        return reviews

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

    processed_data = []
    for restaurant in data:
        processed_restaurant = {}
        for key, value in restaurant.items():
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
                processed_restaurant[new_key] = convert_reviews(value)
            else:
                processed_restaurant[new_key] = value
        processed_data.append(processed_restaurant)

    return processed_data

def add_coordinates_to_restaurants(restaurants: List[Dict]) -> List[Dict]:
    """
    Ajoute les coordonnées GPS aux données des restaurants.
    :param restaurants: Liste de dictionnaires représentant les restaurants.
    :return: Liste de restaurants avec coordonnées ajoutées.
    """
    for restaurant in restaurants:
        address = restaurant.get("address", "")
        name = restaurant.get("name", "")
        coordinates = get_coordinates(address, name)

        restaurant["latitude"] = coordinates["latitude"]
        restaurant["longitude"] = coordinates["longitude"]

    return restaurants

def split_address(data):
    """
    Divise le champ 'address' d'une liste de dictionnaires en 'street', 'postal_code', 'city', et 'country'.
    
    :param data: Liste de dictionnaires contenant un champ 'address'.
    :return: Liste de dictionnaires mise à jour.
    """
    for item in data:
        try:
            street, postal_city = item['address'].split(',', 1)
            postal_code, city_country = postal_city.strip().split(' ', 1)
            city, country = city_country.rsplit(' ', 1)
            item['street'] = street.strip()
            item['postal_code'] = postal_code.strip()
            item['city'] = city.strip()
            item['country'] = country.strip()
        except ValueError:
            item['street'] = item['address']
            item['postal_code'] = None
            item['city'] = None
            item['country'] = None
        del item['address']  # Supprime le champ 'address' original
    return data


# Lecture des données brutes depuis le fichier JSON

with open("data/raw/top_restaurants.json", "r", encoding="utf-8") as file:
    raw_data = json.load(file)

# Prétraitement des données
processed_data = preprocess_restaurant_data(raw_data)

# Ajout des coordonnées GPS
restaurants_with_coordinates = add_coordinates_to_restaurants(processed_data)

#Séparation des adresses
restaurants_final = split_address(restaurants_with_coordinates)

# Sauvegarde des données prétraitées dans un fichier JSON
with open("data/processed/top_restaurants_processed.json", "w", encoding="utf-8") as file:
    json.dump(restaurants_final, file, ensure_ascii=False, indent=4)
