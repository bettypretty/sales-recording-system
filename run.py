from flask import Flask, render_template, request, redirect, flash
from app.database import create_tables, get_db_connection


# Create Flask application
app = Flask(
    __name__,
    template_folder="app/templates",
    static_folder="app/static"
)

# Secret key for Flask flash messages
app.secret_key = "sales-recording-system-secret"


# Create database tables
create_tables()



# Dashboard route

@app.route("/")
def dashboard():

    # Connect to the database
    connection = get_db_connection()

    # Get total number of products
    total_products = connection.execute(
        "SELECT COUNT(*) FROM products"
    ).fetchone()[0]

    # Get total revenue from all sales
    total_revenue = connection.execute(
        "SELECT COALESCE(SUM(total), 0) FROM sales"
    ).fetchone()[0]

    # Get total quantity of products sold
    total_sales = connection.execute(
        "SELECT COALESCE(SUM(quantity), 0) FROM sales"
    ).fetchone()[0]

    # Get today's sales count
    todays_sales = connection.execute(
        """
        SELECT COUNT(*)
        FROM sales
        WHERE DATE(date) = DATE('now')
        """
    ).fetchone()[0]

    # Get recent sales
    recent_sales = connection.execute(
        """
        SELECT *
        FROM sales
        WHERE DATE(date) = DATE('now')
        ORDER BY id DESC
        LIMIT 5
        """
    ).fetchall()

    # Close database connection
    connection.close()

    # Send the information to dashboard.html
    return render_template(
        "dashboard.html",
        total_products=total_products,
        total_revenue=total_revenue,
        total_sales=total_sales,
        todays_sales=todays_sales,
        recent_sales=recent_sales
    )



# Products route

@app.route("/products")
def products():

    # Connect to the database
    connection = get_db_connection()

    # Get all products from the database
    products = connection.execute(
        "SELECT * FROM products ORDER BY id DESC"
    ).fetchall()

    # Close the database connection
    connection.close()

    # Send products to the HTML page
    return render_template(
        "products.html",
        products=products
    )



# Sales route

@app.route("/sales")
def sales():

    # Connect to the database
    connection = get_db_connection()

    # Get all recorded sales
    sales = connection.execute(
        "SELECT * FROM sales ORDER BY id DESC"
    ).fetchall()

    # Close connection
    connection.close()

    # Send sales to the page
    return render_template(
        "sales.html",
        sales=sales
    )



# Reports route


@app.route("/reports")
def reports():

    # Connect to the database
    connection = get_db_connection()

    # Get total number of products
    total_products = connection.execute(
        "SELECT COUNT(*) FROM products"
    ).fetchone()[0]

    # Get total revenue from all sales
    total_revenue = connection.execute(
        "SELECT COALESCE(SUM(total), 0) FROM sales"
    ).fetchone()[0]

    # Get total quantity of products sold
    total_sales = connection.execute(
        "SELECT COALESCE(SUM(quantity), 0) FROM sales"
    ).fetchone()[0]

    # Get today's sales count
    todays_sales = connection.execute(
        """
        SELECT COUNT(*)
        FROM sales
        WHERE DATE(date) = DATE('now')
        """
    ).fetchone()[0]

    # Get complete sales history
    sales = connection.execute(
        """
        SELECT *
        FROM sales
        ORDER BY id DESC
        """
    ).fetchall()

    # Close database connection
    connection.close()

    # Send the information to reports.html
    return render_template(
        "reports.html",
        total_products=total_products,
        total_revenue=total_revenue,
        total_sales=total_sales,
        todays_sales=todays_sales,
        sales=sales
    )


# Add Product route

@app.route("/add_product", methods=["GET", "POST"])
def add_product():

    if request.method == "POST":

        # Get information from the form
        name = request.form["name"]
        category = request.form["category"]
        price = request.form["price"].replace(",", "")
        price = float(price)
        quantity = request.form["quantity"]

        # Connect to the database
        connection = get_db_connection()

        # Add the product to the database
        connection.execute(
            """
            INSERT INTO products (name, category, price, quantity)
            VALUES (?, ?, ?, ?)
            """,
            (name, category, price, quantity)
        )

        # Save changes
        connection.commit()

        # Close connection
        connection.close()

        # Return to Products page
        return redirect("/products")

    # Show Add Product form
    return render_template("add_product.html")



# Delete Product route

@app.route("/delete_product/<int:product_id>", methods=["POST"])
def delete_product(product_id):

    # Connect to the database
    connection = get_db_connection()

    # Delete the selected product
    connection.execute(
        "DELETE FROM products WHERE id = ?",
        (product_id,)
    )

    # Save the change
    connection.commit()

    # Close the database connection
    connection.close()

    # Return to Products page
    return redirect("/products")



# Edit Product route

@app.route("/edit_product/<int:product_id>", methods=["GET", "POST"])
def edit_product(product_id):

    # Connect to the database
    connection = get_db_connection()

    # If the form is submitted
    if request.method == "POST":

        # Get the updated information
        name = request.form["name"]
        category = request.form["category"]
        price = request.form["price"]
        quantity = request.form["quantity"]

        # Update the product
        connection.execute(
            """
            UPDATE products
            SET name = ?, category = ?, price = ?, quantity = ?
            WHERE id = ?
            """,
            (name, category, price, quantity, product_id)
        )

        # Save changes
        connection.commit()

        # Close connection
        connection.close()

        # Return to Products page
        return redirect("/products")

    # Get the product we want to edit
    product = connection.execute(
        "SELECT * FROM products WHERE id = ?",
        (product_id,)
    ).fetchone()

    # Close connection
    connection.close()

    # Open the edit form
    return render_template(
        "edit_product.html",
        product=product
    )



# Record Sale route


@app.route("/record_sale", methods=["GET", "POST"])
def record_sale():

    # Connect to database
    connection = get_db_connection()

    # If form is submitted
    if request.method == "POST":

        # Get product and quantity
        product_id = request.form["product_id"]
        quantity = int(request.form["quantity"])

        # Get selected product
        product = connection.execute(
            "SELECT * FROM products WHERE id = ?",
            (product_id,)
        ).fetchone()

        # Check if product exists
        if product is None:

            connection.close()

            flash("Product not found.", "error")

            return redirect("/record_sale")

        # Check available stock
        if quantity > product["quantity"]:

            # Show error message
            flash(
                f"Insufficient stock. Only {product['quantity']} items available.",
                "error"
            )

            # Close database connection
            connection.close()

            # Return to Record Sale page
            return redirect("/record_sale")

        # Calculate total
        total = product["price"] * quantity

        # Save the sale
        connection.execute(
            """
            INSERT INTO sales (product_name, quantity, total)
            VALUES (?, ?, ?)
            """,
            (product["name"], quantity, total)
        )

        # Reduce product stock
        connection.execute(
            """
            UPDATE products
            SET quantity = quantity - ?
            WHERE id = ?
            """,
            (quantity, product_id)
        )

        # Save changes
        connection.commit()

        # Close connection
        connection.close()

        # Return to Sales page
        return redirect("/sales")

    # Get all products
    products = connection.execute(
        "SELECT * FROM products ORDER BY name"
    ).fetchall()

    # Close connection
    connection.close()

    # Show Record Sale form
    return render_template(
        "record_sale.html",
        products=products
    )



# Start application


if __name__ == "__main__":
    app.run(debug=True)