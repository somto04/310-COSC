import pytest 
from app.routers.reviewRoute import getReview, postReview, getReviews, putReview, removeReview
from app.services.reviewService import ReviewCreate
from main import app

client = TestClient(app)

def test_getReview():
    response = client.get("/reviews/1")
    assert response.status_code == 200
    assert response.json() == "this is a review about avengers end game and i thought it was terrible"

def test_getReviews():
    response = client.get("/reviews/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_postReview():
    payload = { 
        "reviewId": 1,
        "reveiwTitle" : "Avengers Endgame is bad",
        "rating" : 1,
        "reviewBody" : "this is a review about avengers end game and i thought it was terrible",
        "flagged" : False
        }
    
    response = client.post("/reviews/", json = payload)
    assert response.status_code == 201
    data = response.json()
    assert data["reviewId"] == 1
    assert data["reviewTitle"] == "Avengers Endgame is bad"

def test_putReview():
    id = 2
    newPayload = {
        "reviewId": 1,
        "rating" : 4,
        "reviewBody" : "i changed my mind it was actually alright"
    }

    response = client.put("/reviews/", json = newPayload)
    assert response.status_code == 201
    data = response.json()
    assert data["reviewId"] == 1
    assert data["reviewBody"] == "i changed my mind it was actually alright"