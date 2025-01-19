from database.create_warehouse import insert_many_to_many_data

def add_restaurant_to_wr(cursor, restaurant: dict):
    """
    Ajoute un restaurant individuel à la base de données SQLite.
    :param cursor: Curseur SQLite.
    :param restaurant: Dictionnaire contenant les données du restaurant.
    """
    # Insérer les données principales du restaurant
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

    # Obtenir l'ID du restaurant inséré
    id_restaurant = cursor.lastrowid
    if not id_restaurant:
        cursor.execute("SELECT id_restaurant FROM restaurants WHERE name = ? AND street = ? AND city = ?", 
                       (restaurant.get('name'), restaurant.get('street'), restaurant.get('city')))
        id_restaurant = cursor.fetchone()[0]

    # Insérer les relations many-to-many pour cuisines, régimes, fonctionnalités et repas
    insert_many_to_many_data(cursor, id_restaurant, restaurant.get('cuisines', "").split(", "), 
                             "restaurant_cuisines", "id_cuisine", "cuisines")
    insert_many_to_many_data(cursor, id_restaurant, restaurant.get('special_diets', "").split(", "), 
                             "restaurant_special_diets", "id_special_diet", "special_diets")
    insert_many_to_many_data(cursor, id_restaurant, restaurant.get('features', "").split(", "), 
                             "restaurant_features", "id_feature", "features")
    insert_many_to_many_data(cursor, id_restaurant, restaurant.get('meals', "").split(", "), 
                             "restaurant_meals", "id_meal", "meals")

    # Insérer les avis associés au restaurant
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
