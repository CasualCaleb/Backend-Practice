from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from models import User
import pytest_asyncio
from main import app
from db import init_db
import pytest
import aiosqlite

@pytest_asyncio.fixture
async def test_db(monkeypatch, tmp_path):
    db_path = tmp_path / 'test.db'
    # Force database.py to use test.db
    monkeypatch.setattr(
        "db.database.DATABASE_PATH",
        db_path
    )

    await init_db()

    yield db_path

@pytest.fixture()
def mock_oauth_token():
    fake_token = {
        'userinfo': {
            'name': 'user123',
            'sub': 'google-user-123',
            'email': 'user123@example.com',
            'username': 'user123',
            'id': '123456789101112131415'
        }
    }

    with patch(
        "routes.auth.oauth.google.authorize_access_token",
        new=AsyncMock(return_value=fake_token),
    ) as mock:
        yield mock

@pytest_asyncio.fixture
async def normal_user(test_db):
    async with aiosqlite.connect(test_db) as db:
        cursor = await db.execute(
            """
            INSERT INTO users (username, role)
            VALUES (?, ?)
            """,
            ("user123", "user")
        )

        user_id = cursor.lastrowid

        await db.execute(
            """
            INSERT INTO oauth_accounts (
                user_id,
                provider,
                provider_id,
                provider_email
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                user_id,
                "google",
                "google-user-123",
                "user123@example.com"
            )
        )

        await db.commit()

    return User(
        id=user_id,
        username="user123",
        role="user"
    )

@pytest_asyncio.fixture
async def admin_user(test_db):
    async with aiosqlite.connect(test_db) as db:
        cursor = await db.execute(
            """
            INSERT INTO users (username, role)
            VALUES (?, ?)
            """,
            ("admin123", "admin")
        )

        user_id = cursor.lastrowid

        await db.execute(
            """
            INSERT INTO oauth_accounts (
                user_id,
                provider,
                provider_id,
                provider_email
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                user_id,
                "google",
                "google-user-123",
                "user123@example.com"
            )
        )

        await db.commit()

    return User(
        id=user_id,
        username="admin123",
        role="admin"
    )

@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client