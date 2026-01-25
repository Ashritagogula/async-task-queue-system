from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_create_task_success():
    response = client.post(
        "/api/tasks",
        json={
            "title": "Unit Test Task",
            "description": "Testing task creation",
            "metadata": {"priority": "low"}
        }
    )

    assert response.status_code == 202
    body = response.json()
    assert "task_id" in body


def test_create_task_empty_title():
    response = client.post(
        "/api/tasks",
        json={
            "title": "",
            "description": "Invalid title"
        }
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Title and description must not be empty"


def test_create_task_empty_description():
    response = client.post(
        "/api/tasks",
        json={
            "title": "Invalid",
            "description": ""
        }
    )

    assert response.status_code == 400
