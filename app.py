from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import os
import random
import string
app = Flask(__name__)
app.secret_key = "supersecretkey"

PROFILE_FILE = "customer_credentials.txt"

# Cakes Data
cakes_list = [
    {"name": "Red Velvet Cake", "price": 12.99, "image": "redvelvet.jpg"},
    {"name": "Chocolate Cake", "price": 10.99, "image": "chocolate.jpg"},
    {"name": "Coffee Cake", "price": 10.55, "image": "coffee-cake.jpg"},
    {"name": "Three Milk Cake", "price": 10.55, "image": "three-milk.jpg"},
    {"name": "Birthday Cake", "price": 11.99, "image": "birthday-cake.jpg"},
    {"name": "Mousse Cake", "price": 12.99, "image": "mousse-cake.jpeg"}
]

def save_credentials(role, username, password):
    filename = f"{role.lower()}_credentials.txt"
    with open(filename, "a") as file:
        file.write(f"{username},{password}\n")

def check_credentials(role, username, password):
    """Check if the username and password exist in the respective file"""
    filename = f"{role.lower()}_credentials.txt"
    if not os.path.exists(filename):
        return False  # If file doesn't exist, no users are registered yet

    with open(filename, "r") as file:
        for line in file:
            parts = line.strip().split(",")
            if len(parts) == 2:  # Ensure the line has exactly two parts
                saved_user, saved_pass = parts
                if saved_user == username and saved_pass == password:
                    return True
    return False


def load_profile(username):
    try:
        with open(PROFILE_FILE, "r") as file:
            for line in file:
                data = line.strip().split(",")
                if data[0] == username:
                    return {
                        "name": data[0],
                        "email": data[1] if len(data) > 1 else "",
                        "contact": data[2] if len(data) > 2 else "",
                        "address": data[3] if len(data) > 3 else ""
                    }
        return {"name": "", "email": "", "contact": "", "address": ""}
    except FileNotFoundError:
        return {"name": "", "email": "", "contact": "", "address": ""}

def save_profile(profile, username):
    updated_lines = []
    found = False
    try:
        with open(PROFILE_FILE, "r") as file:
            lines = file.readlines()
        for line in lines:
            data = line.strip().split(",")
            if data[0] == username:
                updated_lines.append(f"{profile['name']},{profile['email']},{profile['contact']},{profile['address']}\n")
                found = True
            else:
                updated_lines.append(line)
        if not found:
            updated_lines.append(f"{profile['name']},{profile['email']},{profile['contact']},{profile['address']}\n")
        with open(PROFILE_FILE, "w") as file:
            file.writelines(updated_lines)
    except FileNotFoundError:
        with open(PROFILE_FILE, "w") as file:
            file.write(f"{profile['name']},{profile['email']},{profile['contact']},{profile['address']}\n")

@app.route("/")
def home():
    if "username" in session:
        return redirect(url_for("cakes"))
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        role = request.form.get("role")
        username = request.form.get("username")
        password = request.form.get("password")
        if check_credentials(role, username, password):
            session["username"] = username
            session["role"] = role
            return redirect(url_for("cakes"))
        else:
            return "Invalid credentials! Try again."
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        role = request.form.get("role")
        username = request.form.get("username")
        password = request.form.get("password")
        if not role or not username or not password:
            return "All fields are required!"
        save_credentials(role, username, password)
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/logout")
def logout():
    session.pop("username", None)
    session.pop("role", None)
    session.pop("cart", None)
    return redirect(url_for("login"))

@app.route("/cakes")
def cakes():
    if "username" not in session:
        return redirect(url_for("login"))
    return render_template("cakes.html", cakes=cakes_list)

@app.route("/cake/<cake_name>")
def cake_details(cake_name):
    cake = next((c for c in cakes_list if c["name"] == cake_name.replace("-", " ")), None)
    if not cake:
        return "Cake not found", 404
    cake["description"] = "Our delicious " + cake["name"].lower() + " is made with the finest ingredients!"
    return render_template("cake_details.html", cake=cake)

@app.route("/profile", methods=["GET", "POST"])
def profile():
    if "username" not in session:
        return redirect(url_for("login"))
    username = session["username"]
    if request.method == "POST":
        profile_data = {
            "name": request.form["name"],
            "email": request.form["email"],
            "contact": request.form["contact"],
            "address": request.form["address"]
        }
        save_profile(profile_data, username)
    profile_data = load_profile(username)
    return render_template("profile.html", profile=profile_data)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/save_cart", methods=["POST"])
def save_cart():
    cart_data = request.get_json()
    session["cart"] = cart_data
    return jsonify({"message": "Cart saved."})

@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    if "username" not in session:
        return redirect(url_for("login"))
    username = session["username"]
    cart = session.get("cart", [])
    profile_data = load_profile(username)
    total = sum(item["price"] * item["quantity"] for item in cart)
    return render_template("checkout.html", cart=cart, total=total, profile=profile_data)

@app.route("/confirm_order", methods=["POST"])
def confirm_order():
    if "username" not in session:
        return redirect(url_for("login"))
    session["cart"] = []
    # Generate a random tracking ID
    tracking_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    message = f"Payment successful! Your order has been placed. Your tracking ID is {tracking_id}."
    return render_template("confirmation.html", message=message)
@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == "POST":
        order_id = request.form["order_id"]
        rating = request.form["rating"]
        comments = request.form["comments"]
        # Save feedback logic here if needed
        flash("Thank you for your feedback!")
        return redirect(url_for("feedback"))
    return render_template("feedback.html")
@app.route("/thank_you")
def thank_you():
    return render_template("thank_you.html")

if __name__ == "__main__":
    app.run(debug=True)



