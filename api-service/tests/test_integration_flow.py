import time
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_full_async_task_flow():
    # Step 1: Submit task
    response = client.post(
        "/api/tasks",
        json={
            "title": "Integration Test",
            "description": "Verify async flow",
            "metadata": {"priority": "high"}
        }
    )

    assert response.status_code == 202
    task_id = response.json()["task_id"]

    # Step 2: Wait for worker to process
    time.sleep(6)

    # Step 3: Fetch task status
    response = client.get(f"/api/tasks/{task_id}")

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "COMPLETED"
    assert data["completed_at"] is not None
