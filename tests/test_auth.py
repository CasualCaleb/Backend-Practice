import pytest
from services import auth_services
from unittest.mock import AsyncMock, patch

def test_login(client):
    # Test Google login
    request = client.get('/api/auth/login/google', follow_redirects=False)
    assert request.status_code in (302, 307)

    # Test Discord login
    request = client.get('/api/auth/login/discord', follow_redirects=False)
    assert request.status_code in (302, 307)

def test_callback(client, standard_user):
    user, oauth_account = standard_user

    with patch(
        'routes.auth.get_oauth_user_data',
        return_value={
            'username': user.username,
            'provider': oauth_account.provider,
            'provider_id': oauth_account.provider_id,
            'provider_email': oauth_account.provider_email
        }
    ):
        client.get('/api/auth/login/google', follow_redirects=False)
        response = client.get('/api/auth/callback/google', follow_redirects=False)
        assert response.status_code in (302, 307)

        response = client.get('/api/users/me')
        assert response.json() == user.model_dump()

def test_logout_reject_logged_out(client):
    response = client.post("/api/auth/logout")
    assert response.status_code == 401

def test_logout_accept_logged_in(client, standard_user, login_user):
    user, oauth_account = standard_user
    login_user(user)

    response = client.post("/api/auth/logout")
    assert response.status_code == 200

    response = client.get("/api/users/me")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_link_oauth_account(client, standard_user, login_user):
    user, oauth_account = standard_user
    login_user(user)

    with patch(
            'routes.auth.get_oauth_user_data',
            return_value={
                'username': 'discord_user123',
                'provider': 'discord',
                'provider_id': 'discord_user123',
                'provider_email': 'user@discord.com'
            }
    ):
        client.get('/api/auth/login/google', follow_redirects=False)
        response = client.get('/api/auth/callback/google', follow_redirects=False)
        assert response.status_code in (302, 307)

        response = client.get('/api/users/me')
        assert response.json() == user.model_dump()

        oauth_accounts = await auth_services.get_oauth_accounts(user)
        assert oauth_accounts[0].user_id and oauth_accounts[1].user_id == user.id