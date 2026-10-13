from fastapi import APIRouter

from db.connection import get_connection
from models import User, CreateUser, OauthAccount, CreateOauthAccount
from pathlib import Path

SCHEMA_PATH = Path(__file__).with_name("schema.sql")

async def init_db() -> None:
    schema = SCHEMA_PATH.read_text(encoding="utf-8")

    async with get_connection() as conn:
        await conn.executescript(schema)

async def get_user_by_id(user_id: int) -> User | None:
    async with get_connection() as conn:
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
    async with get_connection() as conn:
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

async def get_oauth_accounts() -> list[OauthAccount]:
    async with get_connection() as conn:
        cursor = await conn.execute("""
            SELECT *
            FROM oauth_accounts
        """)

        oauth_accounts = [
            OauthAccount(
                id=row[0],
                user_id=row[1],
                provider=row[2],
                provider_id=row[3],
                provider_email=row[4]
            ) for row in await cursor.fetchall()
        ]

        return oauth_accounts

async def create_user_with_oauth(create_user: CreateUser, create_oauth_account: CreateOauthAccount) -> tuple[User, OauthAccount]:
    async with get_connection() as conn:
        cursor = await conn.execute("""
            INSERT INTO users (username, role)
            VALUES (?, ?)
        """, (
            create_user.username,
            create_user.role
            )
        )

        user = User(
            id=cursor.lastrowid,
            username=create_user.username,
            role=create_user.role
        )

        cursor = await conn.execute("""
            INSERT INTO oauth_accounts (user_id, provider, provider_id, provider_email)
            VALUES (?, ?, ?, ?)
        """, (
            user.id,
            create_oauth_account.provider,
            create_oauth_account.provider_id,
            create_oauth_account.provider_email
            )
        )

        oauth_account = OauthAccount(
            id=cursor.lastrowid,
            user_id=user.id,
            provider=create_oauth_account.provider,
            provider_id=create_oauth_account.provider_id,
            provider_email=create_oauth_account.provider_email
        )

        await conn.commit()

        return user, oauth_account

async def link_oauth_account(user: User, create_oauth_account: CreateOauthAccount) -> OauthAccount:
    async with get_connection() as conn:
        cursor = await conn.execute("""
            INSERT INTO oauth_accounts(user_id, provider, provider_id, provider_email)
            VALUES (?, ?, ?, ?)
        """, (
            user.id,
            create_oauth_account.provider,
            create_oauth_account.provider_id,
            create_oauth_account.provider_email
            )
        )

        await conn.commit()

        return OauthAccount(
            id=cursor.lastrowid,
            user_id=user.id,
            provider=create_oauth_account.provider,
            provider_id=create_oauth_account.provider_id,
            provider_email=create_oauth_account.provider_email
        )

async def get_oauth_account(provider: str, provider_id: str) -> OauthAccount | None:
    async with get_connection() as conn:
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

async def get_oauth_accounts_by_user_id(user_id: int) -> list[OauthAccount]:
    async with get_connection() as conn:
        cursor = await conn.execute("""
            SELECT *
            FROM oauth_accounts
            WHERE user_id = ?
        """, (user_id,))

        oauth_accounts = [
            OauthAccount(
                id=row[0],
                user_id=row[1],
                provider=row[2],
                provider_id=row[3],
                provider_email=row[4]
            ) for row in await cursor.fetchall()
        ]

        return oauth_accounts

async def update_username(user_id: int, username: str) -> bool:
    async with get_connection() as conn:
        cursor = await conn.execute("""
            UPDATE users
            SET username = ?
            WHERE id = ?;
        """, (username, user_id))

        await conn.commit()

        return cursor.rowcount > 0

async def delete_user(user_id: int) -> bool:
    async with get_connection() as conn:
        cursor = await conn.execute("""
            DELETE FROM users WHERE id = ?
        """, (user_id,))

        await conn.commit()

        return cursor.rowcount > 0

async def log_activity(user_id: int, action: str, details: str) -> bool:
    async with get_connection() as conn:
        cursor = await conn.execute("""
        INSERT INTO activity_log(user_id, action, details)
        VALUES (?, ?, ?)
        """, (user_id, action, details))

        await conn.commit()

        return cursor.rowcount > 0