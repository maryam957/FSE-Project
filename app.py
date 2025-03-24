from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Change this in production

# Dummy user database
users = {"admin": "password123"}

# Cakes Data
cakes_list = [
    {"name": "Red Velvet Cake", "price": 12.99, "image": "redvelvet.jpg"},
    {"name": "Chocolate Cake", "price": 10.99, "image": "chocolate.jpg"},
    {"name": "Coffee Cake", "price": 10.55, "image": "coffee-cake.jpg"},
    {"name": "Three Milk Cake", "price": 10.55, "image": "three-milk.jpg"},
    {"name": "Birthday Cake", "price": 11.99, "image": "birthday-cake.jpg"},
    {"name": "Mousse Cake", "price": 12.99, "image": "mousse-cake.jpeg"}
]


@app.route("/")
def home():
    if "username" in session:
        return redirect(url_for("cakes"))
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        if username in users and users[username] == password:
            session["username"] = username  # Store session
            return redirect(url_for("cakes"))
        else:
            return "Invalid credentials! Try again."

    return render_template("login.html")

@app.route("/cakes")
def cakes():
    if "username" not in session:
        return redirect(url_for("login"))  # Redirect if not logged in
    return render_template("cakes.html", cakes=cakes_list)  # Fixed variable name

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
