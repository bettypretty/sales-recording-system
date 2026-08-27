# database.py

# Handles the connection between the Flask app and SQLite database

import sqlite3
import os


# Location of the SQLite database folder
DATABASE_FOLDER = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "database"
)

# Create the database folder if it does not exist
os.makedirs(DATABASE_FOLDER, exist_ok=True)

# Location of the SQLite database file
DATABASE = os.path.join(DATABASE_FOLDER, "sales.db")


def get_db_connection():
    """
    Creates and returns a connection to the SQLite database.
    """

    connection = sqlite3.connect(DATABASE)

    # Allows database rows to be accessed by column name
    connection.row_factory = sqlite3.Row

    return connection


def create_tables():
    """
    Creates the required database tables if they do not already exist.
    """

    connection = get_db_connection()
    cursor = connection.cursor()

    # Create the users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    """)

    # Create the products table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            quantity INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # Create the sales table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            product_name TEXT NOT NULL,
            category TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            total REAL NOT NULL,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # Add user_id to products if it is missing
    try:
        cursor.execute(
            "ALTER TABLE products ADD COLUMN user_id INTEGER"
        )
    except sqlite3.OperationalError:
        pass

    # Add user_id to sales if it is missing
    try:
        cursor.execute(
            "ALTER TABLE sales ADD COLUMN user_id INTEGER"
        )
    except sqlite3.OperationalError:
        pass

    connection.commit()
    connection.close()