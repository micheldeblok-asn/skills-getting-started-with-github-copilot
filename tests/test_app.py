from fastapi.testclient import TestClient

from src.app import app, activities


def setup_function():
    activities["Chess Club"]["participants"] = [
        "michael@mergington.edu",
        "daniel@mergington.edu",
    ]


def test_unregister_participant():
    client = TestClient(app)

    response = client.delete(
        "/activities/Chess Club/unregister?email=daniel@mergington.edu"
    )

    assert response.status_code == 200
    assert "daniel@mergington.edu" not in activities["Chess Club"]["participants"]
    assert response.json()["message"] == "Removed daniel@mergington.edu from Chess Club"
