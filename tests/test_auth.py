import pytest
from db import get_oauth_account

def test_login(client, normal_user, mock_oauth_identity, oauth_identities):
    # Test Google login
    mock_oauth_identity.return_value = oauth_identities['google']
    request = client.get('/api/auth/login/google', follow_redirects=False)
    assert request.status_code in (302, 307)

    # Test Discord login
    mock_oauth_identity.return_value = oauth_identities['discord']
    request = client.get('/api/auth/login/discord', follow_redirects=False)
    assert request.status_code in (302, 307)

def test_callback(client, normal_user, mock_oauth_identity, oauth_identities):
    mock_oauth_identity.return_value = oauth_identities['google']
    client.get("/api/auth/login/google", follow_redirects=False)
    response = client.get('/api/auth/callback/google', follow_redirects=False)
    assert response.status_code in (302, 307)

    location = response.headers.get('Location')
    assert '/api/users/me' in location

def test_logout_reject_logged_out(client):
    response = client.post("/api/auth/logout")
    assert response.status_code == 401

def test_logout_accept_logged_in(client, normal_user, mock_oauth_identity, oauth_identities):
    mock_oauth_identity.return_value = oauth_identities['google']
    client.get("/api/auth/login/google", follow_redirects=False)
    client.get("/api/auth/callback/google", follow_redirects=False)

    response = client.post("/api/auth/logout")
    assert response.status_code == 200

    response = client.get("/api/users/me")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_link_oauth_account(client, normal_user, mock_oauth_identity, oauth_identities):
    # Login with Google
    mock_oauth_identity.return_value = oauth_identities['google']
    client.get("/api/auth/login/google", follow_redirects=False)
    response = client.get("/api/auth/callback/google", follow_redirects=False)
    assert response.status_code in (302, 307)

    # Link Discord
    mock_oauth_identity.return_value = oauth_identities['discord']
    client.get("/api/auth/login/discord", follow_redirects=False)
    response = client.get("/api/auth/callback/discord", follow_redirects=False)
    assert response.status_code in (302, 307)

    # Get the Oauth accounts from the database and ensure they exist
    google_account = await get_oauth_account('google', oauth_identities['google']['provider_id'])
    discord_account = await get_oauth_account('discord', oauth_identities['discord']['provider_id'])
    assert google_account is not None
    assert discord_account is not None

    # Make sure the Oauth accounts are linked with the User account
    assert google_account.user_id == normal_user.id
    assert discord_account.user_id == normal_user.id