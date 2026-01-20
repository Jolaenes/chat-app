# 🗨️ Chat App (Flask + SQLite)
Prosty projekt aplikacji czatu napisany w Python (Flask) z użyciem SQLite.

---

## Funkcjonalności

- Rejestracja użytkowników
- Logowanie i sesje użytkownika
- Wylogowanie
- Tworzenie czatów prywatnych
- Dodawanie użytkowników do czatu
- Lista czatów użytkownika
- Wysyłanie wiadomości
- Historia wiadomości
- Wiadomości w czasie rzeczywistym (Socket.IO)
- UI
- Obsługa błędów systemowych z komunikatami
- Logowanie zdarzeń

---

## Technologie

- Python 3
- Flask
- SQLite
- HTML + CSS + JavaScript
- Git (feature branches)
- Flask-SocketIO
- Socket.IO (client)

---

## 📁 Struktura projektu

```
chat-app/
│
├── app.py
├── models.py
├── database.db
│
├── templates/
│   ├── login.html
│   ├── register.html
│   └── chat.html
├── static/
│   └── styles.css
├── .gitignore
├── README.md
└── venv/
```

---

## Baza danych

### Tabele:
- users
- chats
- messages
- chat_users

---

## Gałęzie

| Gałąź | Opis |
|-----|-----|
| feature/database | Dzień 2 – baza danych |
| feature/register | Dzień 3 – rejestracja |
| feature/login | Dzień 4 – logowanie |
| feature/chat | Dzień 5 – czaty |
| feature/messages | Dzień 6 i 7 – wiadomości |
| feature/UI | Dzień 8 – interfejs użytkownika |
| feature/logs | Dzień 9 – obsługa błędów i logowanie zdarzeń |

---

## ▶️ Uruchomienie

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux / macOS
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

Aplikacja:
http://127.0.0.1:5000/login

