
def test_admin_rejects_logged_out(client):
    response = client.get('api/admin/users')
    assert response.status_code == 401

def test_admin_rejects_user(client, normal_user, mock_google_token):
    response = client.get('/api/auth/callback', follow_redirects=False)
    assert response.status_code in (302, 307)

    response = client.get('/api/admin/users', follow_redirects=False)
    assert response.status_code == 403

def test_admin_accepts_admin(client, admin_user, mock_google_token):
    response = client.get('/api/auth/callback', follow_redirects=False)
    assert response.status_code in (302, 307)

    response = client.get('/api/admin/users')
    assert response.status_code == 200