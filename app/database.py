
# database.py

# Handles the connection between the Flask app and SQLite database

import sqlite3


# Location of the SQLite database file
DATABASE = "database/sales.db"


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

    # Create the products table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            quantity INTEGER NOT NULL
        )
    """)

    # Create the sales table
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

    # Save the changes to the database
    connection.commit()

    # Close the database connection
    connection.close()
