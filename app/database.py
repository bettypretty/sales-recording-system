# database.py
# Handles the connection between the Flask app and SQLite database

import sqlite3



DATABASE = "database/sales.db"



def get_db_connection():
    connection = sqlite3.connect(DATABASE)

    
    connection.row_factory = sqlite3.Row

    return connection



def create_tables():
    connection = get_db_connection()

    cursor = connection.cursor()


    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            quantity INTEGER NOT NULL
        )
    """)


    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            category TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            total REAL NOT NULL,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    
    connection.commit()

    
    connection.close()