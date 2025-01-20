import sqlite3

def get_db_connection(db_path="src/database/restaurants.db"):
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    return connection
