import sqlite3
import bcrypt

DB_PATH = "users.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def signup(username, email, password):

    username = username.strip()
    email = email.strip().lower()

    if not username or not email or not password:
        return False, "All fields are required."

    if len(password) < 6:
        return False, "Password must contain at least 6 characters."

    password_hash = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    )

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO users
            (username, email, password_hash)
            VALUES (?, ?, ?)
        """, (
            username,
            email,
            password_hash.decode("utf-8")
        ))

        conn.commit()
        conn.close()

        return True, "Account created successfully!"

    except sqlite3.IntegrityError:
        return False, "Username or email already exists."

    except Exception as e:
        return False, f"Signup error: {e}"


def login(username_or_email, password):

    username_or_email = username_or_email.strip()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, username, email, password_hash
        FROM users
        WHERE username = ? OR email = ?
    """, (
        username_or_email,
        username_or_email.lower()
    ))

    user = cursor.fetchone()

    conn.close()

    if user is None:
        return False, None, "Invalid username/email or password."

    user_id = user[0]
    username = user[1]
    email = user[2]
    password_hash = user[3]

    password_correct = bcrypt.checkpw(
        password.encode("utf-8"),
        password_hash.encode("utf-8")
    )

    if password_correct:
        user_data = {
            "id": user_id,
            "username": username,
            "email": email
        }

        return True, user_data, "Login successful!"

    return False, None, "Invalid username/email or password."