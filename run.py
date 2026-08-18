from flask import Flask, render_template, request, redirect, flash, session
from app.database import create_tables, get_db_connection


# Create Flask application
app = Flask(
    __name__,
    template_folder="app/templates",
    static_folder="app/static"
)

# Secret key for Flask sessions and flash messages
app.secret_key = "sales-recording-system-secret"


# Create database tables
create_tables()


# Check if user is logged in
def login_required():

    if "user_id" not in session:

        flash("Please login first.", "error")

        return redirect("/login")

    return None


# DASHBOARD
@app.route("/")
def dashboard():

    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    connection = get_db_connection()

    # Total number of products for the logged-in user
    total_products = connection.execute(
        """
        SELECT COUNT(*)
        FROM products
        WHERE user_id = ?
        """,
        (user_id,)
    ).fetchone()[0]

    # Total revenue for the logged-in user
    total_revenue = connection.execute(
        """
        SELECT COALESCE(SUM(total), 0)
        FROM sales
        WHERE user_id = ?
        """,
        (user_id,)
    ).fetchone()[0]

    # Total quantity sold by the logged-in user
    total_sales = connection.execute(
        """
        SELECT COALESCE(SUM(quantity), 0)
        FROM sales
        WHERE user_id = ?
        """,
        (user_id,)
    ).fetchone()[0]

    # Today's sales count
    todays_sales = connection.execute(
        """
        SELECT COUNT(*)
        FROM sales
        WHERE user_id = ?
        AND DATE(date) = DATE('now')
        """,
        (user_id,)
    ).fetchone()[0]

    # Recent sales
    recent_sales = connection.execute(
        """
        SELECT *
        FROM sales
        WHERE user_id = ?
        AND DATE(date) = DATE('now')
        ORDER BY id DESC
        LIMIT 5
        """,
        (user_id,)
    ).fetchall()

    connection.close()

    return render_template(
        "dashboard.html",
        total_products=total_products,
        total_revenue=total_revenue,
        total_sales=total_sales,
        todays_sales=todays_sales,
        recent_sales=recent_sales
    )

# PRODUCTS
@app.route("/products")
def products():

    login_check = login_required()

    if login_check:
        return login_check
    
    user_id = session["user_id"]

    connection = get_db_connection()

    products = connection.execute(
        "SELECT * FROM products WHERE user_id = ? ORDER BY id DESC""",
    (user_id,)).fetchall()

    connection.close()

    return render_template(
        "products.html",
        products=products
    )


# SALES
@app.route("/sales")
def sales():

    login_check = login_required()

    if login_check:
        return login_check
    user_id = session["user_id"]

    connection = get_db_connection()

    sales = connection.execute(
        "SELECT * FROM sales WHERE user_id = ? ORDER BY id DESC""",
    (user_id,)).fetchall()

    connection.close()

    return render_template(
        "sales.html",
        sales=sales
    )

# REPORTS
@app.route("/reports")
def reports():

    login_check = login_required()

    if login_check:
        return login_check

    user_id = session["user_id"]

    connection = get_db_connection()

    # Total number of products for this user
    total_products = connection.execute(
        """
        SELECT COUNT(*)
        FROM products
        WHERE user_id = ?
        """,
        (user_id,)
    ).fetchone()[0]

    # Total revenue for this user
    total_revenue = connection.execute(
        """
        SELECT COALESCE(SUM(total), 0)
        FROM sales
        WHERE user_id = ?
        """,
        (user_id,)
    ).fetchone()[0]

    # Total quantity sold by this user
    total_sales = connection.execute(
        """
        SELECT COALESCE(SUM(quantity), 0)
        FROM sales
        WHERE user_id = ?
        """,
        (user_id,)
    ).fetchone()[0]

    # Today's sales count for this user
    todays_sales = connection.execute(
        """
        SELECT COUNT(*)
        FROM sales
        WHERE user_id = ?
        AND DATE(date) = DATE('now')
        """,
        (user_id,)
    ).fetchone()[0]

    # Sales belonging only to this user
    sales = connection.execute(
        """
        SELECT *
        FROM sales
        WHERE user_id = ?
        ORDER BY id DESC
        """,
        (user_id,)
    ).fetchall()

    connection.close()

    return render_template(
        "reports.html",
        total_products=total_products,
        total_revenue=total_revenue,
        total_sales=total_sales,
        todays_sales=todays_sales,
        sales=sales
    )

 # ADD PRODUCT
@app.route("/add_product", methods=["GET", "POST"])
def add_product():

    login_check = login_required()

    if login_check:
        return login_check

    if request.method == "POST":

        name = request.form["name"]
        category = request.form["category"]

        price = request.form["price"].replace(",", "")
        price = float(price)

        quantity = request.form["quantity"]

        connection = get_db_connection()
        user_id = session["user_id"]
        connection.execute(
            """
            INSERT INTO products (user_id , name, category, price, quantity)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id,name, category, price, quantity)
        )

        connection.commit()
        connection.close()

        return redirect("/products")

    return render_template("add_product.html")


 # DELETE PRODUCT
@app.route("/delete_product/<int:product_id>", methods=["POST"])
def delete_product(product_id):

    login_check = login_required()

    if login_check:
        return login_check

    user_id = session["user_id"]

    connection = get_db_connection()

    connection.execute(
        """
        DELETE FROM products
        WHERE id = ?
        AND user_id = ?
        """,
        (product_id, user_id)
    )

    connection.commit()
    connection.close()

    return redirect("/products")

 # EDIT PRODUCT
@app.route("/edit_product/<int:product_id>", methods=["GET", "POST"])
def edit_product(product_id):

    login_check = login_required()

    if login_check:
        return login_check

    user_id = session["user_id"]

    connection = get_db_connection()

    if request.method == "POST":

        name = request.form["name"]
        category = request.form["category"]
        price = request.form["price"].replace(",", "")
        price = float(price)
        quantity = request.form["quantity"]

        connection.execute(
            """
            UPDATE products
            SET name = ?, category = ?, price = ?, quantity = ?
            WHERE id = ?
            AND user_id = ?
            """,
            (
                name,
                category,
                price,
                quantity,
                product_id,
                user_id
            )
        )

        connection.commit()
        connection.close()

        return redirect("/products")

    product = connection.execute(
        """
        SELECT *
        FROM products
        WHERE id = ?
        AND user_id = ?
        """,
        (product_id, user_id)
    ).fetchone()

    connection.close()

    return render_template(
        "edit_product.html",
        product=product
    )

# RECORD SALE
@app.route("/record_sale", methods=["GET", "POST"])
def record_sale():

    print("RECORD SALE USER ID:", session.get("user_id"))

    login_check = login_required()

    if login_check:
        return login_check

    user_id = session["user_id"]

    connection = get_db_connection()

    if request.method == "POST":

        product_id = request.form["product_id"]
        quantity = int(request.form["quantity"])

        # Find the product only if it belongs to the logged-in user
        product = connection.execute(
            """
            SELECT *
            FROM products
            WHERE id = ?
            AND user_id = ?
            """,
            (product_id, user_id)
        ).fetchone()

        if product is None:

            connection.close()

            flash("Product not found.", "error")

            return redirect("/record_sale")

        if quantity > product["quantity"]:

            flash(
                f"Insufficient stock. Only {product['quantity']} items available.",
                "error"
            )

            connection.close()

            return redirect("/record_sale")

        total = product["price"] * quantity

        # Record the sale under the logged-in user's account
        connection.execute(
            """
            INSERT INTO sales
            (user_id, product_name, category, quantity, total)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                user_id,
                product["name"],
                product["category"],
                quantity,
                total
            )
        )

        # Reduce the stock of the user's product
        connection.execute(
            """
            UPDATE products
            SET quantity = quantity - ?
            WHERE id = ?
            AND user_id = ?
            """,
            (quantity, product_id, user_id)
        )

        connection.commit()
        connection.close()

        return redirect("/sales")

    # Show only this user's products
    products = connection.execute(
        """
        SELECT *
        FROM products
        WHERE user_id = ?
        ORDER BY name
        """,
        (user_id,)
    ).fetchall()

    connection.close()

    return render_template(
        "record_sale.html",
        products=products
    )

# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():

   
    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        connection = get_db_connection()

        user = connection.execute(
            """
            SELECT *
            FROM users
            WHERE email = ? AND password = ?
            """,
            (email, password)
        ).fetchone()

        connection.close()

        if user:

            session["user_id"] = user["id"]

            session["username"] = user["username"]

            return redirect("/")

        else:

            flash(
                "Invalid email or password.",
                "error"
            )

            return redirect("/login")

    return render_template("login.html")


  # CREATE ACCOUNT
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:

            flash(
                "Passwords do not match.",
                "error"
            )

            return redirect("/register")

        connection = get_db_connection()

        existing_user = connection.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        ).fetchone()

        if existing_user:

            connection.close()

            flash(
                "Username already exists.",
                "error"
            )

            return redirect("/register")

        existing_email = connection.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        ).fetchone()

        if existing_email:

            connection.close()

            flash(
                "Email already exists.",
                "error"
            )

            return redirect("/register")

        connection.execute(
            """
            INSERT INTO users (username, email, password)
            VALUES (?, ?, ?)
            """,
            (username, email, password)
        )

        connection.commit()
        connection.close()

        flash(
            "Account created successfully. Please login.",
            "success"
        )

        return redirect("/login")

    return render_template("create_account.html")


  # LOGOUT
@app.route("/logout")
def logout():

    session.clear()

    flash(
        "You have been logged out.",
        "success"
    )

    return redirect("/login")


# FORGOT PASSWORD
@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    
    if request.method == "POST":
        email = request.form["email"]
        
        connection = get_db_connection()
        
        user = connection.execute(
    "SELECT * FROM users WHERE email = ?",
    (email,)
).fetchone()
        connection.close()
        if user:

            session["reset_user_id"] = user["id"]

            return redirect("/reset-password")

        else:

         flash(
                "No account found with that email.",
                "error"
            )

    return render_template ("forgot_password.html")


# Reset Password

@app.route("/reset-password", methods=["GET", "POST"])
def reset_password():

    if "reset_user_id" not in session:
        return redirect("/forgot-password")

    if request.method == "POST":

        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:

            flash(
                "Passwords do not match.",
                "error"
            )

            return redirect("/reset-password")

        connection = get_db_connection()

        connection.execute(
            """
            UPDATE users
            SET password = ?
            WHERE id = ?
            """,
            (
                password,
                session["reset_user_id"]
            )
        )

        connection.commit()
        connection.close()

        session.pop("reset_user_id", None)

        flash(
            "Password reset successfully. Please login.",
            "success"
        )

        return redirect("/login")

    return render_template("reset_password.html")
 # START APPLICATION
if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
    