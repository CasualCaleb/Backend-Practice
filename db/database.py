from models import User
import sqlite3
from pathlib import Path

db_url = Path(__file__).resolve().parent.parent / "db" / "users.db"

# Create table if missing
def init_db():
    with sqlite3.connect(db_url) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users(
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                google_id TEXT NOT NULL UNIQUE,
                username TEXT,
                email TEXT NOT NULL UNIQUE,
                role TEXT NOT NULL DEFAULT 'user'
            )
        """)

def get_users() -> list[User]:
    with sqlite3.connect(db_url) as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()

        users = [
            User(
                id=row[0],
                google_id=row[1],
                username=row[2],
                email=row[3],
                role=row[4]
            )
            for row in rows
        ]
    return users

def get_user_by_google_id(google_id: str) -> User:
    with sqlite3.connect(db_url) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT *
            FROM users
            WHERE google_id = ?;
        """, (google_id,))

        row = cursor.fetchone()

        if row is None:
            return None

        return User(
            id=row[0],
            google_id=row[1],
            username=row[2],
            email=row[3],
            role=row[4]
        )

def get_user_by_id(user_id: int) -> User:
    conn = sqlite3.connect(db_url)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM users
        WHERE id = ?
    """, (user_id,))
    row = cursor.fetchone()

    if row is None:
        return None

    return User(
        id = row[0],
        google_id=row[1],
        username=row[2],
        email=row[3],
        role=row[4]
    )

def update_username(user_id: int, username: str) -> bool:
    with sqlite3.connect(db_url) as conn:
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE users
            SET username = ?
            WHERE ID = ?;
        """, (username, user_id))

        return cursor.rowcount > 0

def add_user(user: User):
    with sqlite3.connect(db_url) as conn:
        cursor = conn.cursor()

        cursor.execute(f"""
        INSERT INTO users (google_id, username, email, role)
        VALUES (?, ?, ?, ?)
        """, (
            user.google_id,
            user.username,
            user.email,
            user.role
            )
        )

def delete_user(user_id: int) -> bool:
    with sqlite3.connect(db_url) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM users WHERE id = ?
        """, (user_id,))

        return cursor.rowcount > 0