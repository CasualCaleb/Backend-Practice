from fastapi import Request
from fastapi.testclient import TestClient
from models import User, OauthAccount, CreateUser, CreateOauthAccount
import pytest_asyncio
from main import app
from db import init_db
from services import auth_services
import pytest

@pytest.fixture
def login_user(client):
    def login(user: User):
        response = client.get(f'/pytest/login/{user.id}')
        assert response.status_code == 200

    return login

@pytest_asyncio.fixture
async def test_database(monkeypatch, tmp_path):
    db_path = tmp_path / 'test.db'
    # Force database.py to use test.db
    monkeypatch.setattr(
        "db.connection.DATABASE_PATH",
        db_path
    )

    await init_db()

    yield db_path

@pytest_asyncio.fixture
async def standard_user(client, test_database):
    registration = await auth_services.register_user(
        CreateUser(
            username="user123",
            role="user"
        ),
        CreateOauthAccount(
            provider="google",
            provider_id="google_user123",
            provider_email="user@gmail.com"
        )
    )

    return registration

@pytest_asyncio.fixture
async def admin_user(client, test_database):
    registration = await auth_services.register_user(
        CreateUser(
            username="admin123",
            role='admin',
        ),
        CreateOauthAccount(
            provider='google',
            provider_id='google_admin123',
            provider_email='admin@gmail.com'
        )
    )

    return registration

@app.get("/pytest/login/{user_id}")
async def test_login(request: Request, user_id: int):
    request.session['user_id'] = user_id
    return {'Ok': True}

@app.get("/pytest/oauth_action/{action}")
async def test_login(request: Request, action: str):
    request.session['oauth_action'] = action
    return {'Ok': True}

@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client