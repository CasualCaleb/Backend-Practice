import pytest
from models import user, OauthAccount
from services import auth_services, user_services
from unittest.mock import AsyncMock, patch
import db.database as database

def test_login(client):
    # Test Google login
    request = client.get('/api/auth/login/google', follow_redirects=False)
    assert request.status_code in (302, 307)

    # Test Discord login
    request = client.get('/api/auth/login/discord', follow_redirects=False)
    assert request.status_code in (302, 307)

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
async def test_callback_login(client, standard_user, test_database):
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
        response = client.get('/api/auth/callback/google', follow_redirects=False)
        assert response.status_code in (302, 307)
        assert len(await database.get_oauth_accounts()) == 1

@pytest.mark.asyncio
async def test_callback_register_new_user(client, test_database):
    with patch(
            'routes.auth.get_oauth_user_data',
            return_value={
                'username': 'billybob',
                'provider': 'google',
                'provider_id': 'googler123',
                'provider_email': 'billy@google.com'
            }
    ):
        response = client.get('/api/auth/callback/google', follow_redirects=False)
        assert response.status_code in (302, 307)

        oauth_account = await auth_services.get_oauth_account('google', 'googler123')
        assert oauth_account
        assert await user_services.get_user(oauth_account.user_id)

@pytest.mark.asyncio
async def test_callback_link_oauth_account(client, standard_user, login_user, test_database):
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
        response = client.get('/api/auth/callback/discord', follow_redirects=False)
        assert response.status_code in (302, 307)

        oauth_accounts = await auth_services.get_oauth_accounts(user)
        assert len(await database.get_oauth_accounts()) == 2
        assert oauth_accounts[0].user_id and oauth_accounts[1].user_id == user.id