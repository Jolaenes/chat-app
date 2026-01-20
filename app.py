from flask import Flask, request, jsonify, render_template, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask import redirect
import sqlite3
from models import init_db  # importujemy init_db()
#DZIEN7
import pytz
from datetime import datetime
from flask_socketio import SocketIO, emit, join_room
import logging

# ==========================
# Dzień 9 – Logging i obsługa błędów
# ==========================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("app.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
app = Flask(__name__)
#DZIEN7
socketio = SocketIO(app, cors_allowed_origins="*")

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
        logging.warning(f"Nieudana próba rejestracji – brak danych")
        return jsonify({"error": "Username and password are required"}), 400
    if len(username) < 3 or len(password) < 6:
        logging.warning(f"Nieudana próba rejestracji – za krótkie dane")
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
        logging.info(f"Rejestracja użytkownika: {username}")
        return jsonify({"message": "User registered successfully"}), 201
    except sqlite3.IntegrityError as e:
        logging.error(f"Błąd przy rejestracji użytkownika {username}: {str(e)}")
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
        logging.warning(f"Nieudane logowanie użytkownika: {username}") 
        return jsonify({"error": "Invalid username or password"}), 401

    # Zapis sesji
    session["user"] = username
    logging.info(f"Zalogowano użytkownika: {username}")
    return jsonify({"redirect": "/chat"}), 200




# SESJA / WYLOGOWANIE

@app.route("/logout")
def logout():
    user = session.get("user", None)
    session.pop("user", None)
    logging.info(f"Wylogowano użytkownika: {user}") 
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


# Dzień 5
# API: pobranie listy wszystkich użytkowników

@app.route("/api/users")
def api_users():
    if "user" not in session:
        return jsonify({"error": "Not logged in"}), 401

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, username FROM users WHERE username != ?", (session["user"],))
    users = [{"id": row[0], "username": row[1]} for row in cursor.fetchall()]
    conn.close()
    return jsonify(users)


# Dzień 5
# API: pobranie listy czatów

@app.route("/api/chats")
def api_chats():
    if "user" not in session:
        return jsonify({"error": "Not logged in"}), 401

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    # tylko czaty, w których uczestniczy użytkownik
    cursor.execute("""
        SELECT c.id, c.name
        FROM chats c
        JOIN chat_users cu ON c.id = cu.chat_id
        JOIN users u ON cu.user_id = u.id
        WHERE u.username = ?
    """, (session["user"],))
    chats = [{"id": row[0], "name": row[1]} for row in cursor.fetchall()]
    conn.close()
    return jsonify(chats)


# Dzień 5
# API: tworzenie czatu z użytkownikami

@app.route("/api/chats", methods=["POST"])
def api_create_chat():
    if "user" not in session:
        return jsonify({"error": "Not logged in"}), 401

    data = request.get_json()
    name = data.get("name")
    user_ids = data.get("user_ids", [])

    if not name or not user_ids:
        logging.warning(f" Nieudana próba tworzenia czatu – brak danych")
        return jsonify({"error": "Name and users are required"}), 400

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    try:
        # tworzymy czat
        cursor.execute("INSERT INTO chats (name) VALUES (?)", (name,))
        chat_id = cursor.lastrowid

        # dodajemy aktualnego użytkownika do czatu
        cursor.execute("SELECT id FROM users WHERE username = ?", (session["user"],))
        current_user_id = cursor.fetchone()[0]
        cursor.execute("INSERT INTO chat_users (chat_id, user_id) VALUES (?, ?)", (chat_id, current_user_id))

        # dodajemy resztę wybranych użytkowników
        for uid in user_ids:
            cursor.execute("INSERT INTO chat_users (chat_id, user_id) VALUES (?, ?)", (chat_id, uid))

        conn.commit()
        conn.close()
        logging.info(f"Utworzono czat '{name}' przez użytkownika {session['user']}")
        return jsonify({"message": "Chat created"}), 201
    except sqlite3.IntegrityError as e:
        logging.error(f"Błąd przy tworzeniu czatu '{name}': {str(e)}")
        conn.close()
        return jsonify({"error": str(e)}), 400

    # ================================
# Dzień 6 – wysyłanie wiadomości
# ================================
@app.route("/api/messages", methods=["POST"])
def api_send_message():
    if "user" not in session:
        return jsonify({"error": "Not logged in"}), 401

    data = request.get_json()
    chat_id = data.get("chat_id")
    content = data.get("content")

    if not chat_id or not content:
        return jsonify({"error": "Chat ID and content are required"}), 400
    tz_pl = pytz.timezone('Europe/Warsaw')
    timestamp = datetime.now(tz_pl).strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # zapis wiadomości w bazie
    cursor.execute(
        "INSERT INTO messages (chat_id, user, content, timestamp) VALUES (?, ?, ?, ?)",
        (chat_id, session["user"], content, timestamp)
    )
    conn.commit()
    conn.close()
    logging.info(f"Wiadomość wysłana w czacie {chat_id} przez {session['user']}")
    return jsonify({"message": "Message sent"}), 201

# ================================
# Dzień 6 – historia wiadomości
# ================================
@app.route("/api/messages/<int:chat_id>")
def api_get_messages(chat_id):
    if "user" not in session:
        return jsonify({"error": "Not logged in"}), 401

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT user, content, timestamp FROM messages WHERE chat_id = ? ORDER BY timestamp",
        (chat_id,)
    )
    rows = cursor.fetchall()
    conn.close()

    messages = [{"user": row[0], "content": row[1], "timestamp": row[2]} for row in rows]
    return jsonify(messages)

# =============== DZIEŃ 7 ======================
# ============ SOCKET EVENTS (REALTIME) ===============
# =====================================================


@socketio.on("join")
def on_join(data):
    join_room(str(data["chat_id"]))

@socketio.on("send_message")
def socket_send_message(data):
    user = session.get("user")  # <-- teraz używamy użytkownika z sesji
    if not user:
        return

    warsaw_tz = pytz.timezone("Europe/Warsaw")
    timestamp = datetime.now(warsaw_tz).strftime("%Y-%m-%d %H:%M:%S")
   
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
  # Generowanie timestamp w strefie Europe/Warsaw
    

    cursor.execute(
        "INSERT INTO messages (chat_id, user, content, timestamp) VALUES (?, ?, ?, ?)",
        (data["chat_id"], user, data["content"], timestamp)
    )
    conn.commit()
    conn.close()
    logging.info(f"Wiadomość wysłana przez {user} w czacie {data['chat_id']} (Socket)") 

    emit("receive_message", {
        "chat_id": data["chat_id"],
        "user": user,
        "content": data["content"],
        "timestamp": timestamp
    }, room=str(data["chat_id"]))



# Uruchomienie serwera
if __name__ == "__main__":
    logging.info("Uruchomienie serwera Flask + SocketIO")
    socketio.run(app, debug=True, port=5000)
