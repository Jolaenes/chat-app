from flask import Flask, request, jsonify, render_template
from werkzeug.security import generate_password_hash
import sqlite3
from models import init_db  # importujemy init_db()

app = Flask(__name__)

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

# Uruchomienie serwera
if __name__ == "__main__":
    app.run(debug=True)
