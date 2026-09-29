from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from models import User, OauthAccount
import pytest_asyncio
from main import app
from db import init_db, add_user, add_oauth_account
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

@pytest_asyncio.fixture
async def normal_user(test_db):
    user = await add_user(User(
        username='user123',
        role='user'
    ))
    await add_oauth_account(OauthAccount(
        user_id=user.id,
        provider='google',
        provider_id='123456789101112131415',
        provider_email='example@example.com'
    ))

    return user

@pytest_asyncio.fixture
async def admin_user(test_db):
    user = await add_user(User(
        username='user123',
        role='admin'
    ))
    await add_oauth_account(OauthAccount(
        user_id=user.id,
        provider='google',
        provider_id='123456789101112131415',
        provider_email='example@example.com'
    ))

    return user

@pytest.fixture()
def mock_oauth_identity():
    with patch(
        "routes.auth.get_oauth_user_data",
        new_callable=AsyncMock,
    ) as mock:
        yield mock

@pytest.fixture()
def oauth_identities():
    return {
        'google': {
            'provider': 'google',
            'username': 'user123',
            'provider_id': '123456789101112131415',
            'provider_email': 'example@example.com',
        },
        'discord': {
            'provider': 'discord',
            'username': 'user123',
            'provider_id': '123456789101112131415',
            'provider_email': 'example@example.com',
        }
    }

@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client