from flask import Flask, render_template, request, redirect, url_for, session
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Change this in production

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
    """Save user credentials in a text file based on role"""
    filename = f"{role.lower()}_credentials.txt"
    with open(filename, "a") as file:
        file.write(f"{username},{password}\n")

def check_credentials(role, username, password):
    """Check if the username and password exist in the respective file"""
    filename = f"{role.lower()}_credentials.txt"
    
    if not os.path.exists(filename):
        return False  # If file doesn't exist, no users are registered yet
    
    with open(filename, "r") as file:
        credentials = file.readlines()
        for cred in credentials:
            saved_user, saved_pass = cred.strip().split(",")
            if saved_user == username and saved_pass == password:
                return True
    return False


def load_profile(username):
    try:
        with open(PROFILE_FILE, "r") as file:
            for line in file:
                data = line.strip().split(",")
                if data[0] == username:  # Match username
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
        role = request.form.get("role")  # Use .get() to avoid KeyError
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
        role = request.form.get("role")  # Use .get() to avoid KeyError
        username = request.form.get("username")
        password = request.form.get("password")

        if not role or not username or not password:
            return "All fields are required!"

        save_credentials(role, username, password)
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/cakes")
def cakes():
    if "username" not in session:
        return redirect(url_for("login"))
    return render_template("cakes.html", cakes=cakes_list)

@app.route("/profile", methods=["GET", "POST"])
def profile():
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]

    if request.method == "POST":
        updated_profile = {
            "name": request.form["name"],
            "email": request.form["email"],
            "contact": request.form["contact"],
            "address": request.form["address"]
        }
        save_profile(updated_profile, username)

    profile_data = load_profile(username)
    return render_template("profile.html", profile=profile_data)

@app.route("/logout")
def logout():
    session.pop("username", None)
    session.pop("role", None)
    return redirect(url_for("login"))

@app.route("/cake/<cake_name>")
def cake_details(cake_name):
    cake = next((c for c in cakes_list if c["name"] == cake_name.replace("-", " ")), None)
    if not cake:
        return "Cake not found", 404
    cake["description"] = "Our delicious " + cake["name"].lower() + " is made with the finest ingredients, perfect for any occasion!"
    return render_template("cake_details.html", cake=cake)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

if __name__ == "__main__":
    app.run(debug=True)
