from models.user import User
import sqlite3

db_url = "db/users.db"

def get_users() -> list[User]:
    conn = sqlite3.connect(db_url)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
    conn.close()

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