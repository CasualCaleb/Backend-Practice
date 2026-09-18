
def test_login(client):
    request = client.get('/api/auth/login', follow_redirects=False)
    assert request.status_code in (302, 307)

    location = request.headers.get('Location')
    assert 'accounts.google.com' in location

def test_callback(client, normal_user, mock_google_token):
    response = client.get('/api/auth/callback', follow_redirects=False)
    assert response.status_code in (302, 307)

    location = response.headers.get('Location')
    assert '/api/users/me' in location

def test_logout_reject_logged_out(client):
    response = client.post("/api/auth/logout")
    assert response.status_code == 401

def test_logout_accept_logged_in(client, normal_user, mock_google_token):
    response = client.get("/api/auth/callback", follow_redirects=False)
    assert response.status_code in (302, 307)

    response = client.post("/api/auth/logout")
    assert response.status_code == 200

    response = client.get("/api/users/me")
    assert response.status_code == 401