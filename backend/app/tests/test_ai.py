import pytest

@pytest.fixture
def auth_token(client):
    client.post(
        "/api/v1/auth/register",
        json={"name": "AI User", "email": "ai@example.com", "password": "password123", "role": "student"}
    )
    res = client.post(
        "/api/v1/auth/login",
        data={"username": "ai@example.com", "password": "password123"}
    )
    return res.json()["access_token"]

@pytest.mark.asyncio
async def test_ai_analyze_endpoint(async_client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = await async_client.post(
        "/api/v1/ai/analyze",
        json={"text": "Necesito implementar el login del sistema"},
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "suggestions" in data
    assert len(data["suggestions"]) > 0
    # Should detect "login" keyword
    titles = [s["title"].lower() for s in data["suggestions"]]
    assert any("login" in title or "jwt" in title for title in titles)
