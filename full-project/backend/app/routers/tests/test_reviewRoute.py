import pytest 
from fastapi.testclient import TestClient
from app.routers.reviewRoute import getReview, postReview, getReviews, putReview, removeReview
from app.services.reviewService import ReviewCreate
from app.app import app
from app.routers.auth import requireAdmin

# mock user for testing overriding the authentication file requiring an admin
app.dependency_overrides[requireAdmin] = lambda: {"username": "testuser", "role": "admin"}

# temporary mock for testing
#def getCurrentUser():
#    return {"username": "testuser", "role": "admin"}

client = TestClient(app)

def test_getReviews():
    response = client.get("/reviews")  
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_postReview():
    payload = {
        "movieId": 1,
        "userId": 1,
        "reviewTitle": "Avengers Endgame is bad",
        "reviewBody": "This is a review about Avengers Endgame and I thought it was terrible",
        "rating": "1",
        "flagged": False
    }

    response = client.post("/reviews", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["reviewTitle"] == payload["reviewTitle"]
    assert data["rating"] == payload["rating"]

def test_getReview():
    # Assuming a review with ID 1 exists after posting
    response = client.get("/reviews/1")
    assert response.status_code in [200, 404]  # depends if ID 1 exists
    if response.status_code == 200:
        assert "reviewBody" in response.json()

def test_putReview():
    review_id = 1
    update_payload = {
        "reviewBody": "I changed my mind, it was actually alright",
        "rating": "4"
    }

    response = client.put(f"/reviews/{review_id}", json=update_payload)
    assert response.status_code in [200, 404]  # if review exists
    if response.status_code == 200:
        data = response.json()
        assert data["reviewBody"] == update_payload["reviewBody"]
        
