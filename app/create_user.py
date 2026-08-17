# Import the database connection function
from app.database import get_db_connection


# Connect to the SQLite database
connection = get_db_connection()


# Insert a new user into the users table
connection.execute(
    """
    INSERT INTO users (username, email, password)
    VALUES (?, ?, ?)
    """,
    ("admin", "admin@example.com", "12345")
)


# Save the changes to the database
connection.commit()


# Close the database connection
connection.close()


# Display a success message
print("User created successfully!")