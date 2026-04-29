import pytest

@pytest.fixture
def auth_token(client):
    client.post(
        "/api/v1/auth/register",
        json={"name": "Proj User", "email": "proj@example.com", "password": "password123", "role": "student"}
    )
    res = client.post(
        "/api/v1/auth/login",
        data={"username": "proj@example.com", "password": "password123"}
    )
    return res.json()["access_token"]

def test_create_project(client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.post(
        "/api/v1/projects",
        json={"name": "Test Project", "description": "A new test project"},
        headers=headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Project"
    assert "id" in data
    
    # Check if 4 columns were automatically created
    proj_id = data["id"]
    response_cols = client.get(f"/api/v1/projects/{proj_id}/columns", headers=headers)
    assert response_cols.status_code == 200
    cols = response_cols.json()
    assert len(cols) == 4
    col_names = [c["name"] for c in cols]
    assert "Pendiente" in col_names
    assert "Finalizada" in col_names
