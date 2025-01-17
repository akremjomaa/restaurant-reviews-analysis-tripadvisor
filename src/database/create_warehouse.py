import json
import sqlite3


def load_json(filepath):
    """
    Charge un fichier JSON et retourne son contenu.
    :param filepath: Chemin du fichier JSON.
    :return: Contenu du fichier JSON sous forme de dictionnaire ou liste.
    """
    with open(filepath, 'r', encoding='utf-8') as file:
        return json.load(file)


def create_tables(cursor):
    """
    Crée les tables SQLite nécessaires pour stocker les données des restaurants,
    en incluant les relations many-to-many et des contraintes pour éviter les doublons.
    :param cursor: Curseur SQLite pour exécuter les commandes SQL.
    """
    # Table principale pour les restaurants
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS restaurants (
        id_restaurant INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
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
        url TEXT,
        UNIQUE(name, street, city)
    );
    ''')

    # Tables annexes pour les données catégoriques
    for table in ["cuisines", "special_diets", "features", "meals"]:
        cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {table} (
            id_{table[:-1]} INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE
        );
        ''')

    # Tables de jointure many-to-many
    for table, reference in [
        ("restaurant_cuisines", "cuisines"),
        ("restaurant_special_diets", "special_diets"),
        ("restaurant_features", "features"),
        ("restaurant_meals", "meals"),
    ]:
        cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {table} (
            id_restaurant INTEGER,
            id_{reference[:-1]} INTEGER,
            FOREIGN KEY (id_restaurant) REFERENCES restaurants (id_restaurant),
            FOREIGN KEY (id_{reference[:-1]}) REFERENCES {reference} (id_{reference[:-1]}),
            UNIQUE(id_restaurant, id_{reference[:-1]})
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
        FOREIGN KEY (id_restaurant) REFERENCES restaurants (id_restaurant),
        UNIQUE(author, review_text, id_restaurant)
    );
    ''')


def insert_many_to_many_data(cursor, restaurant_id, items, table_name, id_column_name, reference_table):
    """
    Insère les relations many-to-many entre les restaurants et leurs catégories associées.
    :param cursor: Curseur SQLite.
    :param restaurant_id: ID du restaurant concerné.
    :param items: Liste des items à associer (exemple : cuisines, régimes spéciaux).
    :param table_name: Nom de la table de jointure.
    :param id_column_name: Nom de la colonne ID dans la table de référence.
    :param reference_table: Table de référence contenant les items.
    """
    for item in items:
        item = item.strip() if isinstance(item, str) else None
        if not item:
            continue

        # Vérifie si l'item existe déjà dans la table de référence
        cursor.execute(f"SELECT {id_column_name} FROM {reference_table} WHERE name = ?", (item,))
        row = cursor.fetchone()

        if row is None:
            # Ajoute l'item à la table de référence
            cursor.execute(f"INSERT INTO {reference_table} (name) VALUES (?)", (item,))
            reference_id = cursor.lastrowid
        else:
            reference_id = row[0]

        # Insère la relation dans la table de jointure
        cursor.execute(f'''
        INSERT OR IGNORE INTO {table_name} (id_restaurant, {id_column_name})
        VALUES (?, ?);
        ''', (restaurant_id, reference_id))


def insert_data(cursor, data):
    """
    Insère les données JSON dans les tables SQLite, en gérant les relations many-to-many.
    :param cursor: Curseur SQLite.
    :param data: Données des restaurants sous forme de liste de dictionnaires.
    """
    for restaurant in data:
        # Prépare les données principales des restaurants
        restaurant_data = (
            restaurant.get('name'),
            restaurant.get('street'),
            restaurant.get('postal_code'),
            restaurant.get('city'),
            restaurant.get('country'),
            restaurant.get('latitude'),
            restaurant.get('longitude'),
            restaurant.get('reviews_count'),
            restaurant.get('overall_rating'),
            restaurant.get('ranking'),
            restaurant.get('cuisine_rating'),
            restaurant.get('service_rating'),
            restaurant.get('qualite_prix_rating'),
            restaurant.get('ambiance_rating'),
            restaurant.get('price_range'),
            restaurant.get('url'),
        )
        cursor.execute('''
        INSERT OR IGNORE INTO restaurants (
            name, street, postal_code, city, country, latitude, longitude,
            reviews_count, overall_rating, ranking, cuisine_rating,
            service_rating, qualite_prix_rating, ambiance_rating, price_range, url
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        ''', restaurant_data)

        # Récupère l'ID du restaurant nouvellement inséré
        id_restaurant = cursor.lastrowid
        if not id_restaurant:
            # Recherche l'ID existant si le restaurant est déjà présent
            cursor.execute("SELECT id_restaurant FROM restaurants WHERE name = ? AND street = ? AND city = ?", 
                           (restaurant.get('name'), restaurant.get('street'), restaurant.get('city')))
            id_restaurant = cursor.fetchone()[0]

        # Insère les relations many-to-many
        insert_many_to_many_data(cursor, id_restaurant, restaurant.get('cuisines', "").split(", "), 
                                 "restaurant_cuisines", "id_cuisine", "cuisines")
        insert_many_to_many_data(cursor, id_restaurant, restaurant.get('special_diets', "").split(", "), 
                                 "restaurant_special_diets", "id_special_diet", "special_diets")
        insert_many_to_many_data(cursor, id_restaurant, restaurant.get('features', "").split(", "), 
                                 "restaurant_features", "id_feature", "features")
        insert_many_to_many_data(cursor, id_restaurant, restaurant.get('meals', "").split(", "), 
                                 "restaurant_meals", "id_meal", "meals")

        # Insère les avis
        for review in restaurant.get('reviews', []):
            review_data = (
                review.get('author'),
                review.get('contributions'),
                review.get('rating'),
                review.get('title'),
                review.get('review_text'),
                review.get('manager_response'),
                review.get('review_date'),
                id_restaurant,
            )
            cursor.execute('''
            INSERT OR IGNORE INTO reviews (
                author, contributions, rating, title, review_text,
                manager_response, review_date, id_restaurant
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            ''', review_data)


def main(json_filepath, sqlite_db_filepath):
    """
    Point d'entrée principal pour créer les tables SQLite et insérer les données depuis un fichier JSON.
    :param json_filepath: Chemin du fichier JSON contenant les données des restaurants.
    :param sqlite_db_filepath: Chemin de la base de données SQLite.
    """
    data = load_json(json_filepath)

    conn = sqlite3.connect(sqlite_db_filepath)
    cursor = conn.cursor()

    create_tables(cursor)
    insert_data(cursor, data)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    json_filepath = "data/processed/top_restaurants_processed.json"
    sqlite_db_filepath = "src/database/restaurants.db"
    main(json_filepath, sqlite_db_filepath)
