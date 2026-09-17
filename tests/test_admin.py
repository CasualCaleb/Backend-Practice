from fastapi import HTTPException
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch
from models.user import User
from routes.admin import require_admin
import pytest

def test_admin_rejects_logged_out(client):
    response = client.get('api/admin/users')
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_admin_rejects_user():
    normal_user = User(
        id=1,
        google_id="user123",
        username="casualcaleb",
        email="caleb@example.com",
        role="user"
    )

    request = SimpleNamespace(
        session={"user_id": 1}
    )

    with patch(
        "routes.admin.get_user_by_id",
        new=AsyncMock(return_value=normal_user)
    ):
        with pytest.raises(HTTPException) as exc:
            await require_admin(request)

    assert exc.value.status_code == 403

@pytest.mark.asyncio
async def test_admin_accepts_admin():
    admin_user = User(
        id=1,
        google_id="user123",
        username="casualcaleb",
        email="caleb@example.com",
        role="admin"
    )

    request = SimpleNamespace(
        session={"user_id": 1}
    )

    with patch(
        "routes.admin.get_user_by_id",
        new=AsyncMock(return_value=admin_user)
    ):
        result = await require_admin(request)
    assert admin_user == result

@pytest.mark.asyncio
async def test_admin_rejects_missing_user():
    request = SimpleNamespace(
        session={"user_id": 1}
    )

    with patch(
        "routes.admin.get_user_by_id",
        new=AsyncMock(return_value=None)
    ):
        with pytest.raises(HTTPException) as exc:
            await require_admin(request)

    assert exc.value.status_code == 404