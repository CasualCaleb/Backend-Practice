
def test_rejects_logged_out(client):
    request = client.get("/api/users/me")
    assert request.status_code == 401

def test_accepts_logged_in(client, standard_user, login_user):
    user, oauth_account = standard_user
    login_user(user)

    response = client.get("/api/users/me")

    assert response.status_code == 200
    assert response.json() == user.model_dump()

def test_me_username(client, standard_user, login_user):
    user, oauth_account = standard_user
    login_user(user)

    response = client.patch(
        "/api/users/me/username",
        json={"username": "updated"}
    )
    assert response.status_code == 200

    # Checks if username was actually updated
    response = client.get("/api/users/me")
    assert response.json()['username'] == "updated"

def test_me_delete(client, standard_user, login_user):
    user, oauth_account = standard_user
    login_user(user)

    response = client.delete('/api/users/me')
    assert response.json() == True

    response = client.get("/api/users/me")
    assert response.status_code == 401