import json
import pandas as pd
from datetime import datetime


def rename_keys(data, rename_map):
    """
    Renomme les clés spécifiées dans le dictionnaire ou les éléments d'une liste.
    :param data: Dictionnaire ou liste contenant les données JSON.
    :param rename_map: Dictionnaire de correspondance {ancienne_clé: nouvelle_clé}.
    :return: Données avec les clés renommées.
    """
    if isinstance(data, dict):
        renamed_data = {}
        for key, value in data.items():
            new_key = rename_map.get(key, key)  # Renomme la clé si elle est dans le rename_map
            renamed_data[new_key] = rename_keys(value, rename_map)
        return renamed_data
    elif isinstance(data, list):
        return [rename_keys(item, rename_map) for item in data]
    else:
        return data  


def preprocess_restaurant_data(json_file):
    """
    Préprocesser les données brutes JSON en DataFrame Pandas.
    """
    with open(json_file, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    restaurant_data = []
    reviews_data = []

    for restaurant in raw_data:
        # Nettoyage des colonnes principales
        name = restaurant.get("name", "Inconnu")
        address = restaurant.get("address", "Inconnu")
        reviews_count = restaurant.get("reviews_count", 0)
        rating = float(restaurant["rating"].replace(",", ".")) if restaurant.get("rating") else None
        ranking = restaurant.get("ranking", None)
        total_restaurants = restaurant.get("total_restaurants", None)

        # Conversion des textes en listes pour standardisation
        cuisines = restaurant.get("CUISINES", "").split(", ") if restaurant.get("CUISINES") else []
        special_diets = restaurant.get("Régimes spéciaux", "").split(", ") if restaurant.get("Régimes spéciaux") else []
        meals = restaurant.get("Repas", "").split(", ") if restaurant.get("Repas") else []

        # Stockage des données principales
        restaurant_data.append({
            "name": name,
            "address": address,
            "reviews_count": reviews_count,
            "rating": rating,
            "ranking": ranking,
            "total_restaurants": total_restaurants,
            "cuisines": cuisines,
            "special_diets": special_diets,
            "meals": meals
        })

        # Prétraitement des avis
        for review in restaurant.get("reviews", []):
            review_date = review.get("review_date", "").replace("Rédigé le ", "").strip()
            review_date = datetime.strptime(review_date, "%d %B %Y").strftime("%Y-%m-%d") if review_date else None
            review_text = review.get("review_text", "")
            sentiment = "positif" if "excellent" in review_text.lower() or "magnifique" in review_text.lower() else \
                        "négatif" if "déception" in review_text.lower() or "mauvais" in review_text.lower() else \
                        "neutre"

            reviews_data.append({
                "restaurant_name": name,
                "author": review.get("author", "Anonyme"),
                "contributions": review.get("contributions", 0),
                "rating": float(review.get("rating", 0)),
                "title": review.get("title", ""),
                "review_text": review_text,
                "review_date": review_date,
                "manager_response": review.get("manager_response", "Aucune réponse"),
                "sentiment": sentiment,
                "text_length": len(review_text)
            })

    # Convertir en DataFrame pour analyse et stockage
    df_restaurants = pd.DataFrame(restaurant_data)
    df_reviews = pd.DataFrame(reviews_data)

    return df_restaurants, df_reviews


# json_file = "data/raw/top_15_restaurants.json"
# df_restaurants, df_reviews = preprocess_restaurant_data(json_file)

# # Sauvegarder les données prétraitées
# df_restaurants.to_csv("data/processed/restaurants.csv", index=False, encoding="utf-8")
# df_reviews.to_csv("data/processed/reviews.csv", index=False, encoding="utf-8")
