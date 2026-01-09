from flask import Flask, request, jsonify, render_template, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask import redirect
import sqlite3
from models import init_db  # importujemy init_db()

app = Flask(__name__)

# Sesja użytkownika
app.secret_key = "dev-secret-key"

# Inicjalizacja bazy przy starcie
init_db()

# Strona główna
@app.route("/")
def home():
    return "Chat działa + baza SQLite gotowa!"

# Formularz rejestracji (GET)
@app.route("/register", methods=["GET"])
def register_form():
    return render_template("register.html")

# Rejestracja użytkownika (POST)
@app.route("/register", methods=["POST"])
def register_user():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    # Walidacja
    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400
    if len(username) < 3 or len(password) < 6:
        return jsonify({"error": "Username min 3 chars, password min 6 chars"}), 400

    hashed_password = generate_password_hash(password)

    try:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, hashed_password)
        )
        conn.commit()
        conn.close()
        return jsonify({"message": "User registered successfully"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Username already exists"}), 400



# LOGOWANIE UŻYTKOWNIKA

# Formularz logowania (GET)
@app.route("/login", methods=["GET"])
def login_form():
    return render_template("login.html")

# Logowanie (POST)
@app.route("/login", methods=["POST"])
def login_user():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT password FROM users WHERE username = ?",
        (username,)
    )
    user = cursor.fetchone()
    conn.close()

    if not user or not check_password_hash(user[0], password):
        return jsonify({"error": "Invalid username or password"}), 401

    # Zapis sesji
    session["user"] = username

    return jsonify({"redirect": "/chat"}), 200




# SESJA / WYLOGOWANIE

@app.route("/logout")
def logout():
    session.pop("user", None)
    return jsonify({"message": "Logged out"}), 200


@app.route("/me")
def me():
    if "user" not in session:
        return jsonify({"error": "Not logged in"}), 401
    return jsonify({"user": session["user"]})

# widok chat
@app.route("/chat")
def chat():
    if "user" not in session:
        return redirect("/login")
    return render_template("chat.html", user=session["user"])


# Uruchomienie serwera
if __name__ == "__main__":
    app.run(debug=True)
