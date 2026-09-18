
def test_rejects_logged_out(client):
    request = client.get("/api/users/me")
    assert request.status_code == 401

def test_accepts_logged_in(client, normal_user, mock_google_token):
    response = client.get("/api/auth/callback", follow_redirects=False)
    assert response.status_code in (302, 307)

    response = client.get("/api/users/me")
    assert response.json() == normal_user.model_dump()

def test_me_username(client, normal_user, mock_google_token):
    response = client.get("/api/auth/callback", follow_redirects=False)
    assert response.status_code in (302, 307)

    response = client.patch(
        "/api/users/me/username",
        json={"username": "updated"}
    )

    assert response.status_code == 200
    assert response.json() == True

    # Checks if username was actually updated
    response = client.get("/api/users/me")

    assert response.status_code == 200
    assert response.json()['username'] == "updated"

def test_me_delete(client, normal_user, mock_google_token):
    response = client.get("/api/auth/callback", follow_redirects=False)
    assert response.status_code in (302, 307)

    response = client.delete('/api/users/me')
    assert response.status_code == 200

    response = client.get("/api/users/me")
    assert response.status_code == 401