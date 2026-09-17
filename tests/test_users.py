from fastapi import HTTPException
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch
from pygments.lexers import data
from models.user import User
from routes.users import require_user
from main import app
import pytest

def test_rejects_logged_out(client):
    request = client.get("/api/users/me")
    assert request.status_code == 401

def test_accepts_logged_in(client):
    normal_user = User(
        id=1,
        google_id="user123",
        username="test",
        email="example@example.com",
        role="user"
    )

    def fake_user():
        return normal_user
    app.dependency_overrides[require_user] = fake_user

    try:
        response = client.get("/api/users/me")

        assert response.status_code == 200
        assert response.json() == normal_user.model_dump()
    finally:
        app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_rejects_invalid_user():
    request = SimpleNamespace(
        session = {"user_id": 1}
    )

    with patch(
        'routes.users.get_user_by_id',
        new=AsyncMock(return_value=None)
    ):
        with pytest.raises(HTTPException) as exc:
            await require_user(request)
    assert exc.value.status_code == 404

@pytest.mark.asyncio
async def test_me_username(client):
    normal_user = User(
        id=1,
        google_id="user123",
        username="default",
        email="example@example.com",
        role="user"
    )
    def fake_user():
        return normal_user

    app.dependency_overrides[require_user] = fake_user

    try:
        with patch(
            'routes.users.update_username',
            new=AsyncMock(return_value=True)
        ) as mock_update, patch(
            'routes.users.log_activity',
            new=AsyncMock()
        ) as mock_log:
            response = client.patch('/api/users/me/username', json={'username': 'updated'})

        assert response.status_code == 200

        mock_update.assert_awaited_once_with(
            1,
            'updated'
        )
        mock_log.assert_awaited_once_with(
            1,
            'username',
            'Changed username to updated'
        )
    finally:
        app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_me_delete(client):
    normal_user = User(
        id=1,
        google_id="user123",
        username="default",
        email="example@example.com",
        role="user"
    )

    def fake_user():
        return normal_user
    app.dependency_overrides[require_user] = fake_user

    try:
        with patch(
            'routes.users.delete_user',
            new=AsyncMock(return_value=True)
        ):
            response = client.delete('/api/users/me')

        assert response.status_code == 200
    finally:
        app.dependency_overrides.clear()