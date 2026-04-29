def test_register_user(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "name": "New User",
            "email": "new@example.com",
            "password": "password123",
            "role": "student"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "new@example.com"
    assert "id" in data

def test_login_user(client, test_user):
    # test_user from fixture is created but we need to ensure the hashed_password matches "password123"
    # Actually test_user has "hashedpassword", so it won't work with normal login unless we register first
    # Let's register a user then login
    client.post(
        "/api/v1/auth/register",
        json={
            "name": "Login Test",
            "email": "logintest@example.com",
            "password": "password123",
            "role": "student"
        }
    )
    
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "logintest@example.com", "password": "password123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client):
    client.post(
        "/api/v1/auth/register",
        json={"name": "P", "email": "p@example.com", "password": "password123", "role": "student"}
    )
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "p@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401
