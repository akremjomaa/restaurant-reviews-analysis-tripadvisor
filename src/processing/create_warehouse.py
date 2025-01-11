import json
import sqlite3
#from pysqlite3 import dbapi2 as sqlite3

# Chargement du fichier JSON
def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        return json.load(file)

# Création des tables SQLite
def create_tables(cursor):
    # Table restaurant
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS restaurants (
        id_restaurant INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        street TEXT,
        postal_code TEXT,
        city TEXT,
        country TEXT,
        latitude REAL,
        longitude REAL,
        reviews_count INTEGER,
        overall_rating REAL,
        ranking INTEGER,
        cuisine_rating REAL,
        service_rating REAL,
        value_rating REAL,
        ambiance_rating REAL,
        price_range TEXT,
        cuisines TEXT,
        special_diets TEXT,
        features TEXT,
        meals TEXT,
        url TEXT
    );
    ''')

    # Table reviews
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS reviews (
        id_review INTEGER PRIMARY KEY AUTOINCREMENT,
        author TEXT,
        contributions INTEGER,
        rating REAL,
        title TEXT,
        review_text TEXT,
        manager_response TEXT,
        review_date TEXT,
        id_restaurant INTEGER,
        FOREIGN KEY (id_restaurant) REFERENCES restaurant (id_restaurant)
    );
    ''')

# Insertion des données dans SQLite
def insert_data(cursor, data):
    for restaurant in data:
        # Extraction des informations de restaurant
        restaurant_data = (
            restaurant.get('name', None),
            restaurant.get('street', None),
            restaurant.get('postal_code', None),
            restaurant.get('city', None),
            restaurant.get('country', None),
            restaurant.get('latitude', None),
            restaurant.get('longitude', None),
            restaurant.get('reviews_count', None),
            restaurant.get('overall_rating', None),
            restaurant.get('ranking', None),
            restaurant.get('cuisine_rating', None),
            restaurant.get('service_rating', None),
            restaurant.get('value_rating', None),
            restaurant.get('ambiance_rating', None),
            restaurant.get('price_range', None),
            restaurant.get('cuisines', None),
            restaurant.get('special_diets', None),
            restaurant.get('features', None),
            restaurant.get('meals', None),
            restaurant.get('url', None)
        )

        # Insertion dans la table restaurant
        cursor.execute('''
        INSERT INTO restaurants (
            name, street, postal_code, city, country, latitude, longitude,
            reviews_count, overall_rating, ranking,
            cuisine_rating, service_rating, value_rating, ambiance_rating,
            price_range, cuisines, special_diets, features, meals, url
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        ''', restaurant_data)

        # Récupération de l'id_restaurant
        id_restaurant = cursor.lastrowid

        # Insertion des reviews
        for review in restaurant.get('reviews', []):
            review_data = (
                review.get('author', None),
                review.get('contributions', None),
                review.get('rating', None),
                review.get('title', None),
                review.get('review_text', None),
                review.get('manager_response', None),
                review.get('review_date', None),
                id_restaurant
            )
            cursor.execute('''
            INSERT INTO reviews (
                author, contributions, rating, title, review_text,
                manager_response, review_date, id_restaurant
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            ''', review_data)

# Fonction principale
def main(json_filepath, sqlite_db_filepath):
    # Charger les données JSON
    data = load_json(json_filepath)

    # Connexion à SQLite
    conn = sqlite3.connect(sqlite_db_filepath)
    cursor = conn.cursor()

    # Créer les tables
    create_tables(cursor)

    # Insérer les données
    insert_data(cursor, data)

    # Sauvegarder et fermer la base de données
    conn.commit()
    conn.close()
    print("Données insérées avec succès dans la base de données SQLite.")

# Exemple d'utilisation
if __name__ == "__main__":
    json_filepath = "top_restaurants_processed.json"  # Remplacez par le chemin de votre fichier JSON
    sqlite_db_filepath = "restaurants.db"  # Chemin du fichier SQLite
    main(json_filepath, sqlite_db_filepath)
