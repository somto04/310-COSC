import pytest
from fastapi.testclient import TestClient
from app.app import app

client = TestClient(app)

#  mock a logged-in admin user if auth is required later
@pytest.fixture(autouse=True)
def mock_auth(monkeypatch):
    from app.routers import auth
    monkeypatch.setattr(auth, "getCurrentUser", lambda: {"id": 1, "username": "testuser", "role": "admin"})


# test listing all reviews
def test_getReviews():
    response = client.get("/reviews")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if data:
        assert "reviewTitle" in data[0]


#  test posting a new review
def test_postReview():
    payload = {
        "movieId": 1,
        "userId": 1,
        "reviewTitle": "Avengers Endgame is bad",
        "reviewBody": "This is a review about Avengers Endgame and I thought it was terrible",
        "rating": 1,      # int now
        "flagged": False
    }

    response = client.post("/reviews", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["reviewTitle"] == payload["reviewTitle"]
    assert data["rating"] == payload["rating"]


#  test getting a specific review by ID
def test_getReview():
    response = client.get("/reviews/1")
    assert response.status_code in [200, 404]
    if response.status_code == 200:
        data = response.json()
        assert "reviewBody" in data
        assert isinstance(data["movieId"], int)


#  test updating a review
def test_putReview():
    review_id = 1
    update_payload = {
        "reviewBody": "I changed my mind, it was actually alright",
        "rating": 4      # int now
    }

    response = client.put(f"/reviews/{review_id}", json=update_payload)
    assert response.status_code in [200, 404]
    if response.status_code == 200:
        data = response.json()
        assert data["reviewBody"] == update_payload["reviewBody"]
        assert data["rating"] == update_payload["rating"]
