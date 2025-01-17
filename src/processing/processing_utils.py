import json
from geopy.geocoders import Nominatim
from geopy.exc import GeopyError
from time import sleep


def load_json(filepath):
    """Charge un fichier JSON."""
    with open(filepath, 'r', encoding='utf-8') as file:
        return json.load(file)


def save_json(data, filepath):
    """Sauvegarde les données dans un fichier JSON."""
    with open(filepath, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def get_coordinates(address, name, geolocator=None, retries=3, delay=2):
    """
    Obtenir les coordonnées GPS d'une adresse ou du nom d'un restaurant.
    :param address: Adresse complète.
    :param name: Nom du restaurant.
    :param geolocator: Instance du géolocalisateur.
    :param retries: Nombre de tentatives en cas d'échec.
    :param delay: Délai initial entre les tentatives.
    :return: Dictionnaire avec latitude et longitude ou None si non trouvé.
    """
    geolocator = geolocator or Nominatim(user_agent="restaurant_locator")
    for attempt in range(retries):
        try:
            location = geolocator.geocode(address, timeout=10)
            if location:
                return {"latitude": location.latitude, "longitude": location.longitude}

            location = geolocator.geocode(name, timeout=10)
            if location:
                return {"latitude": location.latitude, "longitude": location.longitude}
        except GeopyError as e:
            print(f"Erreur Geopy : {e}. Tentative {attempt + 1}/{retries}.")
            sleep(delay)
            delay *= 2
    return {"latitude": None, "longitude": None}
