import copy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


BASE_ACTIVITIES = copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    activities.clear()
    activities.update(copy.deepcopy(BASE_ACTIVITIES))


def test_get_activities_returns_all_activity_details():
    # Given
    client = TestClient(app)

    # When
    response = client.get("/activities")

    # Then
    assert response.status_code == 200
    payload = response.json()
    assert "Chess Club" in payload
    assert payload["Chess Club"]["participants"] == [
        "michael@mergington.edu",
        "daniel@mergington.edu",
    ]


def test_signup_adds_email_to_selected_activity():
    # Given
    client = TestClient(app)
    email = "newstudent@mergington.edu"

    # When
    response = client.post(f"/activities/Chess Club/signup?email={email}")

    # Then
    assert response.status_code == 200
    assert email in activities["Chess Club"]["participants"]
    assert response.json()["message"] == f"Signed up {email} for Chess Club"


def test_signup_rejects_duplicate_email_for_same_activity():
    # Given
    client = TestClient(app)
    email = "daniel@mergington.edu"

    # When
    response = client.post(f"/activities/Chess Club/signup?email={email}")

    # Then
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"
    assert activities["Chess Club"]["participants"].count(email) == 1


def test_signup_rejects_when_activity_is_full():
    # Given
    client = TestClient(app)
    activities["Chess Club"]["participants"] = [f"student{i}@mergington.edu" for i in range(12)]

    # When
    response = client.post("/activities/Chess Club/signup?email=overflow@mergington.edu")

    # Then
    assert response.status_code == 400
    assert response.json()["detail"] == "Activity is full"
    assert "overflow@mergington.edu" not in activities["Chess Club"]["participants"]


def test_signup_returns_not_found_for_missing_activity():
    # Given
    client = TestClient(app)

    # When
    response = client.post("/activities/Unknown Club/signup?email=student@mergington.edu")

    # Then
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_removes_email_from_activity():
    # Given
    client = TestClient(app)
    email = "daniel@mergington.edu"

    # When
    response = client.delete(f"/activities/Chess Club/unregister?email={email}")

    # Then
    assert response.status_code == 200
    assert email not in activities["Chess Club"]["participants"]
    assert response.json()["message"] == f"Removed {email} from Chess Club"


def test_unregister_rejects_email_not_in_activity():
    # Given
    client = TestClient(app)
    email = "notregistered@mergington.edu"

    # When
    response = client.delete(f"/activities/Chess Club/unregister?email={email}")

    # Then
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"
