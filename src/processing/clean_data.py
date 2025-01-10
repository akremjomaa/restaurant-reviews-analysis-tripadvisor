import json
from typing import List, Dict


def preprocess_restaurant_data(data: List[Dict]) -> List[Dict]:
    """
    Prétraite les données des restaurants pour ajuster les noms des attributs et les types de données.
    :param data: Liste de dictionnaires représentant les données des restaurants.
    :return: Liste de dictionnaires avec les noms d'attributs et les types mis à jour.
    """
    def convert_price_range(price_range: str) -> str:
        """
        Convertit une plage de prix en un format normalisé (par ex., "25.00-30.00").
        :param price_range: Plage de prix brute sous forme de chaîne.
        :return: Plage de prix normalisée sous forme de chaîne.
        """
        try:
            return price_range.replace("\u202f", "").replace(",", ".").replace("€", "").strip()
        except Exception:
            return price_range

    def convert_reviews(reviews: List[Dict]) -> List[Dict]:
        """
        Convertit les types de données des avis et standardise les formats.
        :param reviews: Liste de dictionnaires représentant les avis bruts.
        :return: Liste de dictionnaires représentant les avis traités.
        """
        for review in reviews:
            review["contributions"] = int(review.get("contributions", 0))
            review["rating"] = float(review.get("rating", 0))
            review["review_date"] = review.get("review_date", "").replace("Rédigé le ", "").strip()
        return reviews

    # Mapping des noms des attributs
    attribute_mapping = {
        "name": "name",
        "address": "address",
        "reviews_count": "reviews_count",
        "rating": "overall_rating",
        "ranking": "ranking",
        "total_restaurants": "total_restaurants",
        "Cuisine": "cuisine_rating",
        "Service": "service_rating",
        "Rapport qualité-prix": "value_rating",
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
            elif new_key in ["cuisine_rating", "service_rating", "value_rating", "ambiance_rating"]:
                processed_restaurant[new_key] = float(value) if value is not None else None
            elif new_key in ["reviews_count", "ranking", "total_restaurants"]:
                processed_restaurant[new_key] = int(value) if value is not None else None
            elif new_key == "reviews":
                processed_restaurant[new_key] = convert_reviews(value)
            else:
                processed_restaurant[new_key] = value
        processed_data.append(processed_restaurant)

    return processed_data

# Lecture des données brutes depuis le fichier JSON

with open("data/raw/top_restaurants.json", "r", encoding="utf-8") as file:
    raw_data = json.load(file)

# Prétraitement des données
processed_data = preprocess_restaurant_data(raw_data)

# Sauvegarde des données prétraitées dans un fichier JSON
with open("data/processed/top_restaurants_processed.json", "w", encoding="utf-8") as file:
    json.dump(processed_data, file, ensure_ascii=False, indent=4)
