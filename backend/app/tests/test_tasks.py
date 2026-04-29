import pytest

@pytest.fixture
def auth_token(client):
    client.post(
        "/api/v1/auth/register",
        json={"name": "Task User", "email": "task@example.com", "password": "password123", "role": "student"}
    )
    res = client.post(
        "/api/v1/auth/login",
        data={"username": "task@example.com", "password": "password123"}
    )
    return res.json()["access_token"]

@pytest.fixture
def project_data(client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    res = client.post(
        "/api/v1/projects",
        json={"name": "Proj", "description": "Desc"},
        headers=headers
    )
    proj = res.json()
    cols_res = client.get(f"/api/v1/projects/{proj['id']}/columns", headers=headers)
    cols = cols_res.json()
    return {"project_id": proj["id"], "col_id": cols[0]["id"]}

def test_create_task(client, auth_token, project_data):
    headers = {"Authorization": f"Bearer {auth_token}"}
    proj_id = project_data["project_id"]
    col_id = project_data["col_id"]
    
    response = client.post(
        f"/api/v1/projects/{proj_id}/tasks",
        json={
            "title": "New Task",
            "description": "Desc",
            "priority": "high",
            "project_id": proj_id,
            "column_id": col_id
        },
        headers=headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "New Task"
    assert data["project_id"] == proj_id

def test_move_task(client, auth_token, project_data):
    headers = {"Authorization": f"Bearer {auth_token}"}
    proj_id = project_data["project_id"]
    col_id = project_data["col_id"]
    
    # Get all cols to find another one
    cols_res = client.get(f"/api/v1/projects/{proj_id}/columns", headers=headers)
    cols = cols_res.json()
    second_col_id = cols[1]["id"]
    
    # Create task
    task_res = client.post(
        f"/api/v1/projects/{proj_id}/tasks",
        json={
            "title": "Task to move",
            "project_id": proj_id,
            "column_id": col_id
        },
        headers=headers
    )
    task_id = task_res.json()["id"]
    
    # Move task
    update_res = client.patch(
        f"/api/v1/tasks/{task_id}",
        json={"column_id": second_col_id},
        headers=headers
    )
    assert update_res.status_code == 200
    assert update_res.json()["column_id"] == second_col_id
