
def test_admin_rejects_logged_out(client):
    response = client.get('api/admin/users')
    assert response.status_code == 401

def test_admin_rejects_user(client, standard_user, login_user):
    user, oauth_account = standard_user
    login_user(user)

    response = client.get('/api/admin/users', follow_redirects=False)

    assert response.status_code == 403

def test_admin_accepts_admin(client, admin_user, login_user):
    user, oauth_account = admin_user
    login_user(user)

    response = client.get('/api/admin/users')
    assert response.status_code == 200

def test_admin_removes_user(client, admin_user, standard_user, login_user):
    user, oauth_account_user = standard_user
    admin_user, oauth_account_admin = admin_user
    login_user(admin_user)

    response = client.get(f'/api/admin/users/{user.id}', follow_redirects=False)
    assert response.status_code == 200

    response = client.delete(f'/api/admin/users/{user.id}', follow_redirects=False)
    assert response.status_code == 200

    response = client.get(f'/api/admin/users/{user.id}', follow_redirects=False)
    assert response.status_code == 404
