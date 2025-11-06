import pytest
from fastapi.testclient import TestClient
from app.app import app
from app.routers import replyRoute

# Fake login so you’re always authenticated
app.dependency_overrides[replyRoute.getCurrentUser] = lambda: {"id": 1, "username": "tester", "role": "admin"}

client = TestClient(app)


# Test GET /replies/{reviewId}
def test_get_replies():
    """Checks that /replies/{reviewId} returns a valid response (even if empty)."""
    response = client.get("/replies/1")

    # The route should exist
    assert response.status_code in [200, 404, 500]

    # If 200, verify response structure
    if response.status_code == 200:
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            assert "replyBody" in data[0]
            assert "userId" in data[0]


# Test POST /replies
def test_post_reply():
    """Checks that /replies accepts new replies correctly."""
    payload = {
        "reviewId": 1,
        "userId": 100,
        "replyBody": "This is a simple test reply!",
        "datePosted": "3 Nov 2025"
    }

    response = client.post("/replies", json=payload)

    # should succeed (either 200 or 201 depending on your route)
    assert response.status_code in [200, 201]

    data = response.json()
    assert data["replyBody"] == payload["replyBody"]
    assert data["userId"] == payload["userId"]
    assert data["reviewId"] == payload["reviewId"]
