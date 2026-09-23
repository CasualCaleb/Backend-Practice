from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from models import User
import pytest_asyncio
from main import app
import aiosqlite
from db import init_db
import pytest

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
def mock_google_token():
    fake_token = {
        'userinfo': {
            'sub': 'user123',
            'name': 'default',
            'email': 'example@example.com',
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
            INSERT INTO users (
                google_id,
                username,
                email,
                role
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                "user123",
                "default",
                "example@example.com",
                "user"
            )
        )

        await db.commit()

        user_id = cursor.lastrowid

    return User(
        id=user_id,
        google_id="user123",
        username="default",
        email="example@example.com",
        role="user"
    )

@pytest_asyncio.fixture
async def admin_user(test_db):
    async with aiosqlite.connect(test_db) as db:
        cursor = await db.execute(
            """
            INSERT INTO users (
                google_id,
                username,
                email,
                role
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                "user123",
                "default",
                "example@example.com",
                "admin"
            )
        )

        await db.commit()

        user_id = cursor.lastrowid

    return User(
        id=user_id,
        google_id="user123",
        username="default",
        email="example@example.com",
        role="admin"
    )

@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client