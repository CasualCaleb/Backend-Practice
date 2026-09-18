from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from models import User
import pytest_asyncio
from main import app
import aiosqlite
import pytest
import os

TEST_DB = "test.db"

@pytest_asyncio.fixture
async def test_db(monkeypatch):
    # Force database.py to use test.db
    monkeypatch.setattr(
        "db.database.DATABASE_PATH",
        TEST_DB
    )

    # Remove leftover DB from a crashed/previous test run
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

    # Create fresh test database
    async with aiosqlite.connect(TEST_DB) as db:
        await db.execute(
            """
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                google_id TEXT UNIQUE NOT NULL,
                username TEXT,
                email TEXT UNIQUE NOT NULL,
                role TEXT DEFAULT 'user'
            )
            """
        )

        await db.execute(
            """
            CREATE TABLE activity_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT,
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        await db.commit()

    yield TEST_DB

    # Cleanup after test
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

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