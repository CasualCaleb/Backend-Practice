from models import User
import aiosqlite
from pathlib import Path

DATABASE_PATH = Path(__file__).resolve().parent.parent / "db" / "database.db"

# Create tables if missing
async def init_db() -> None:
    async with aiosqlite.connect(DATABASE_PATH) as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                google_id TEXT NOT NULL UNIQUE,
                username TEXT,
                email TEXT NOT NULL UNIQUE,
                role TEXT NOT NULL DEFAULT 'user'
            )
        """)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS activity_log(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT NOT NULL,
                details TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        await conn.commit()

async def log_activity(user_id: int, action: str, details: str) -> None:
    async with aiosqlite.connect(DATABASE_PATH) as conn:
        await conn.execute("""
        INSERT INTO activity_log(user_id, action, details)
        VALUES (?, ?, ?)
        """, (user_id, action, details))

        await conn.commit()

async def get_users() -> list[User]:
    async with aiosqlite.connect(DATABASE_PATH) as conn:
        cursor = await conn.execute("""
            SELECT id, google_id, username, email, role
            FROM users
        """)
        rows = await cursor.fetchall()

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

async def get_user_by_google_id(google_id: str) -> User | None:
   async with aiosqlite.connect(DATABASE_PATH) as conn:
        cursor = await conn.execute("""
            SELECT id, google_id, username, email, role
            FROM users
            WHERE google_id = ?;
        """, (google_id,))

        row = await cursor.fetchone()

        if row is None:
            return None

        return User(
            id=row[0],
            google_id=row[1],
            username=row[2],
            email=row[3],
            role=row[4]
        )

async def get_user_by_id(user_id: int) -> User | None:
    async with aiosqlite.connect(DATABASE_PATH) as conn:
        cursor = await conn.execute("""
            SELECT id, google_id, username, email, role
            FROM users
            WHERE id = ?
        """, (user_id,))
        row = await cursor.fetchone()

        if row is None:
            return None

        return User(
            id=row[0],
            google_id=row[1],
            username=row[2],
            email=row[3],
            role=row[4]
        )

async def update_username(user_id: int, username: str) -> bool:
    async with aiosqlite.connect(DATABASE_PATH) as conn:
        cursor = await conn.execute("""
            UPDATE users
            SET username = ?
            WHERE id = ?;
        """, (username, user_id))

        await conn.commit()

        return cursor.rowcount > 0

async def add_user(user: User) -> bool:
    async with aiosqlite.connect(DATABASE_PATH) as conn:
        cursor = await conn.execute("""
        INSERT INTO users (google_id, username, email, role)
        VALUES (?, ?, ?, ?)
        """, (
            user.google_id,
            user.username,
            user.email,
            user.role
            )
        )

        await conn.commit()

        return cursor.rowcount > 0

async def delete_user(user_id: int) -> bool:
    async with aiosqlite.connect(DATABASE_PATH) as conn:
        cursor = await conn.execute("""
            DELETE FROM users WHERE id = ?
        """, (user_id,))

        await conn.commit()

        return cursor.rowcount > 0