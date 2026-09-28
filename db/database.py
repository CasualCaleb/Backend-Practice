from models import User, OauthAccount
import aiosqlite
from pathlib import Path
import asyncio

DATABASE_PATH = Path(__file__).resolve().parent.parent / "db" / "database.db"

# Create tables if missing
async def init_db() -> None:
    async with aiosqlite.connect(DATABASE_PATH) as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                role TEXT NOT NULL DEFAULT 'user'
            )
        """)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS oauth_accounts(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                provider TEXT NOT NULL,
                provider_id TEXT NOT NULL,
                provider_email TEXT,
                
                FOREIGN KEY (user_id)
                    REFERENCES users(id)
                    ON DELETE CASCADE,
                    
                UNIQUE(provider, provider_id),
                UNIQUE(user_id, provider)
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

async def get_user_by_id(user_id: int) -> User | None:
    async with aiosqlite.connect(DATABASE_PATH) as conn:
        cursor = await conn.execute("""
            SELECT id, username, role
            FROM users
            WHERE id = ?
        """, (user_id,))
        row = await cursor.fetchone()

        if row is None:
            return None

        return User(
            id=row[0],
            username=row[1],
            role=row[2]
        )

async def get_users() -> list[User]:
    async with aiosqlite.connect(DATABASE_PATH) as conn:
        cursor = await conn.execute("""
            SELECT *
            FROM users
        """)
        rows = await cursor.fetchall()

        users = [
            User(
                id=row[0],
                username=row[1],
                role=row[2]
            )
            for row in rows
        ]
    return users

async def add_user(user: User) -> User:
    async with aiosqlite.connect(DATABASE_PATH) as conn:
        cursor = await conn.execute("""
            INSERT INTO users (username, role)
            VALUES (?, ?)
        """, (
            user.username,
            user.role
            )
        )

        await conn.commit()

        return User(
            id=cursor.lastrowid,
            username=user.username,
            role=user.role
        )

async def add_oauth_account(oauth_account: OauthAccount) -> OauthAccount:
    async with aiosqlite.connect(DATABASE_PATH) as conn:
        cursor = await conn.execute("""
            INSERT INTO oauth_accounts(user_id, provider, provider_id, provider_email)
            VALUES (?, ?, ?, ?)
        """, (
            oauth_account.user_id,
            oauth_account.provider,
            oauth_account.provider_id,
            oauth_account.provider_email
            )
        )

        await conn.commit()

        return OauthAccount(
            id=cursor.lastrowid,
            user_id=oauth_account.user_id,
            provider=oauth_account.provider,
            provider_id=oauth_account.provider_id,
            provider_email=oauth_account.provider_email
        )

async def get_oauth_account(provider: str, provider_id: str) -> OauthAccount | None:
    async with aiosqlite.connect(DATABASE_PATH) as conn:
        cursor = await conn.execute("""
            SELECT *
            FROM oauth_accounts
            WHERE provider = ? AND provider_id = ?
        """, (provider, provider_id,))

        row = await cursor.fetchone()

        if row is None:
            return None

        return OauthAccount(
            id=row[0],
            user_id=row[1],
            provider=row[2],
            provider_id=row[3],
            provider_email=row[4],
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

async def delete_user(user_id: int) -> bool:
    async with aiosqlite.connect(DATABASE_PATH) as conn:
        cursor = await conn.execute("""
            DELETE FROM users WHERE id = ?
        """, (user_id,))

        await conn.commit()

        return cursor.rowcount > 0

async def log_activity(user_id: int, action: str, details: str) -> None:
    async with aiosqlite.connect(DATABASE_PATH) as conn:
        await conn.execute("""
        INSERT INTO activity_log(user_id, action, details)
        VALUES (?, ?, ?)
        """, (user_id, action, details))

        await conn.commit()