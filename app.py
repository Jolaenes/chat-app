from flask import Flask
from models import init_db

app = Flask(__name__)

# inicjalizacja bazy przy starcie aplikacji
init_db()

@app.route("/")
def home():
    return "Chat działa + baza SQLite gotowa!"

if __name__ == "__main__":
    app.run(debug=True)
