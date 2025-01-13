import json
import sqlite3

# Chargement du fichier JSON
def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        return json.load(file)

# Création des tables SQLite
def create_tables(cursor):
    # Table principale pour les restaurants
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
        qualite_prix_rating REAL,
        ambiance_rating REAL,
        price_range TEXT,
        url TEXT
    );
    ''')

    # Table pour les cuisines
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS cuisines (
        id_cuisine INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE
    );
    ''')

    # Table pour les régimes spéciaux
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS special_diets (
        id_special_diet INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE
    );
    ''')

    # Table pour les fonctionnalités
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS features (
        id_feature INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE
    );
    ''')

    # Table pour les repas
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS meals (
        id_meal INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE
    );
    ''')

    # Tables de jointure many-to-many
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS restaurant_cuisines (
        id_restaurant INTEGER,
        id_cuisine INTEGER,
        FOREIGN KEY (id_restaurant) REFERENCES restaurants (id_restaurant),
        FOREIGN KEY (id_cuisine) REFERENCES cuisines (id_cuisine),
        PRIMARY KEY (id_restaurant, id_cuisine)
    );
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS restaurant_special_diets (
        id_restaurant INTEGER,
        id_special_diet INTEGER,
        FOREIGN KEY (id_restaurant) REFERENCES restaurants (id_restaurant),
        FOREIGN KEY (id_special_diet) REFERENCES special_diets (id_special_diet),
        PRIMARY KEY (id_restaurant, id_special_diet)
    );
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS restaurant_features (
        id_restaurant INTEGER,
        id_feature INTEGER,
        FOREIGN KEY (id_restaurant) REFERENCES restaurants (id_restaurant),
        FOREIGN KEY (id_feature) REFERENCES features (id_feature),
        PRIMARY KEY (id_restaurant, id_feature)
    );
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS restaurant_meals (
        id_restaurant INTEGER,
        id_meal INTEGER,
        FOREIGN KEY (id_restaurant) REFERENCES restaurants (id_restaurant),
        FOREIGN KEY (id_meal) REFERENCES meals (id_meal),
        PRIMARY KEY (id_restaurant, id_meal)
    );
    ''')

    # Table pour les avis
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
        FOREIGN KEY (id_restaurant) REFERENCES restaurants (id_restaurant)
    );
    ''')

# Insérer des valeurs uniques dans une table
def insert_unique_values(cursor, table_name, column_name, values):
    id_map = {}
    for value in values:
        cursor.execute(f"INSERT OR IGNORE INTO {table_name} ({column_name}) VALUES (?)", (value,))
        cursor.execute(f"SELECT rowid FROM {table_name} WHERE {column_name} = ?", (value,))
        id_map[value] = cursor.fetchone()[0]
    return id_map

def insert_many_to_many_data(cursor, restaurant_id, items, table_name, id_column_name, reference_table):
    """
    Insère des relations many-to-many entre restaurants et items.
    :param cursor: Curseur de la base de données SQLite.
    :param restaurant_id: ID du restaurant.
    :param items: Liste d'items à insérer.
    :param table_name: Nom de la table de relation.
    :param id_column_name: Nom de la colonne ID dans la table de relation.
    :param reference_table: Nom de la table de référence (e.g., features, meals).
    """
    for item in items:
        # Nettoyage des données
        item = item.strip() if isinstance(item, str) else None
        if not item:  # Ignorer les items vides ou None
            continue

        # Vérifier si l'item existe déjà dans la table de référence
        cursor.execute(f"SELECT {id_column_name} FROM {reference_table} WHERE name = ?", (item,))
        row = cursor.fetchone()

        # Si l'item n'existe pas, l'insérer
        if row is None:
            cursor.execute(f"INSERT INTO {reference_table} (name) VALUES (?)", (item,))
            reference_id = cursor.lastrowid
        else:
            reference_id = row[0]

        # Insérer la relation dans la table many-to-many
        cursor.execute(f"""
        INSERT INTO {table_name} (id_restaurant, {id_column_name})
        VALUES (?, ?)
        """, (restaurant_id, reference_id))


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
            restaurant.get('qualite_prix_rating', None),
            restaurant.get('ambiance_rating', None),
            restaurant.get('price_range', None),
            restaurant.get('url', None)
        )

        # Insertion dans la table restaurants
        cursor.execute('''
        INSERT INTO restaurants (
            name, street, postal_code, city, country, latitude, longitude,
            reviews_count, overall_rating, ranking,
            cuisine_rating, service_rating, qualite_prix_rating, ambiance_rating,
            price_range, url
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        ''', restaurant_data)

        # Récupérer l'ID du restaurant
        id_restaurant = cursor.lastrowid

        # Insertion des relations many-to-many
        insert_many_to_many_data(cursor, id_restaurant, restaurant.get('cuisines', "").split(", "), 
                                 "restaurant_cuisines", "id_cuisine", "cuisines")
        insert_many_to_many_data(cursor, id_restaurant, restaurant.get('special_diets', "").split(", "), 
                                 "restaurant_special_diets", "id_special_diet", "special_diets")
        insert_many_to_many_data(cursor, id_restaurant, restaurant.get('features', "").split(", "), 
                                 "restaurant_features", "id_feature", "features")
        insert_many_to_many_data(cursor, id_restaurant, restaurant.get('meals', "").split(", "), 
                                 "restaurant_meals", "id_meal", "meals")

        # Insertion des avis
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
    json_filepath = "data/processed/top_restaurants_processed.json"  
    sqlite_db_filepath = "restaurants.db"
    main(json_filepath, sqlite_db_filepath)
