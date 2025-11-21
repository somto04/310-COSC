"""
Integration Tests for Review Router

This file contains integration tests for the review API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI, status, HTTPException
from unittest.mock import patch
from app.app import app
from app.routers.reviewRoute import router, getCurrentUser
from app.schemas.review import Review, ReviewCreate, ReviewUpdate

# SETUP & FIXTURES
@pytest.fixture
def app():
    """Create a FastAPI app instance for testing"""
    app = FastAPI()
    app.include_router(router)
    return app


@pytest.fixture
def client(app):
    """Create a test client for making HTTP requests"""
    return TestClient(app)


@pytest.fixture
def sample_review_data():
    """Sample review data for testing"""
    return Review(
        id= 1,
        movieId= 1,
        userId= 1,
        username= "testuser",
        reviewTitle= "Great Movie!",
        reviewBody= "This movie was amazing, highly recommend",
        rating= 5,
        flagged= False
    )


@pytest.fixture
def sample_reviews_list(sample_review_data):
    """Sample list of reviews for testing"""
    return [
        sample_review_data,
        Review(
            id= 2,
            movieId= 1,
            userId= 2,
            username= "anotheruser",
            reviewTitle= "Not bad",
            reviewBody= "It was okay, nothing special",
            rating= 3,
            flagged= False
        ),
        Review(
            id= 3,
            movieId= 2,
            userId= 1,
            username= "testuser",
            reviewTitle= "Disappointed",
            reviewBody= "Expected better from this film",
            rating= 2,
            flagged= False
        )
    ]

class FakeUser:
    def __init__(self, id, username, role):
        self.id = id
        self.username = username
        self.role = role

# ============================================================================ #
# INTEGRATION TESTS
# ============================================================================ #

class TestReviewRouterIntegration:
    """Integration tests for review API endpoints"""

    @patch('app.routers.reviewRoute.listReviews')
    def test_get_all_reviews_endpoint(self, mock_list, client, sample_reviews_list):
        mock_list.return_value = sample_reviews_list

        response = client.get("/reviews")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert data[0]["reviewTitle"] == "Great Movie!"
        assert data[1]["reviewTitle"] == "Not bad"

    @patch('app.routers.reviewRoute.getReviewById')
    def test_get_review_by_id_endpoint(self, mock_get, client, sample_review_data):
        mock_get.return_value = sample_review_data

        response = client.get("/reviews/1")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["reviewTitle"] == "Great Movie!"
        assert data["rating"] == 5
        mock_get.assert_called_once_with(1)

    @patch('app.routers.reviewRoute.getReviewById')
    def test_get_review_by_id_not_found(self, mock_get, client):
        mock_get.side_effect = HTTPException(status_code=404, detail="Review not found")

        response = client.get("/reviews/999")

        assert response.status_code == 404
        assert response.json()["detail"] == "Review not found"

    @patch('app.routers.reviewRoute.searchReviews')
    def test_search_reviews_with_query(self, mock_search, client, sample_review_data):
        mock_search.return_value = [sample_review_data]

        response = client.get("/reviews/search", params={"query": "great"})
        mock_search.assert_called_once_with("great")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["reviewTitle"] == "Great Movie!"
        mock_search.assert_called_once_with("great")

    @patch('app.routers.reviewRoute.searchReviews')
    def test_search_reviews_with_limit_and_offset(self, mock_search, client, sample_reviews_list):
        mock_search.return_value = sample_reviews_list

        response = client.get("/reviews/search?query=movie&limit=2&offset=1")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["id"] == 2  # now int, not str

    @patch('app.routers.reviewRoute.createReview')
    def test_create_review_endpoint(self, mock_create, client, sample_review_data, app):
        """Test POST /reviews creates a new review"""
        # Arrange
        mock_create.return_value = sample_review_data

        new_review = ReviewCreate(
            movieId= 1,
            reviewTitle= "Great Movie!",
            reviewBody= "This movie was amazing, highly recommend",
            rating= 5
        )
        
        app.dependency_overrides[getCurrentUser] = lambda: FakeUser(id=1, username="testuser", role="user")
        
        # Send request with auth header
        response = client.post("/reviews", 
                             json=new_review.model_dump(),
                             headers={"Authorization": "Bearer testuser"})

        assert response.status_code == 201
        data = response.json()
        assert data["reviewTitle"] == "Great Movie!"
        assert data["rating"] == 5

    @patch('app.routers.reviewRoute.updateReview')
    @patch('app.routers.reviewRoute.getReviewById')
    def test_update_review_endpoint(self, mock_get_review, mock_update, client, sample_review_data, app):
        """Test PUT /reviews/{id} updates a review.
        It verifies that the FastAPI route for updating a review correctly
        updates an existing review's data and returns the modified view. 
        """
        # Arrange
        # Mock getting the existing review (for ownership check)
        mock_get_review.return_value = sample_review_data
        
        # Set up expected updated review
        updated_review = sample_review_data.copy()
        updated_review.reviewBody = "Updated review text"
        updated_review.rating = 4
        mock_update.return_value = updated_review

        update_data = ReviewUpdate(
            reviewBody= "Updated review text",
            rating= 4
        )

        app.dependency_overrides[getCurrentUser] = lambda: FakeUser(id=1, username="testuser", role="user")

        response = client.put("/reviews/1", 
                            json=update_data.model_dump(),
                            headers={"Authorization": "Bearer testuser"})
        
        # Assert
        app.dependency_overrides = {}

        assert response.status_code == 200
        data = response.json()
        assert data["reviewBody"] == "Updated review text"
        assert data["rating"] == 4

    @patch('app.routers.reviewRoute.deleteReview')
    @patch('app.routers.reviewRoute.getReviewById')
    def test_delete_review_as_admin(self, mock_get_review, mock_delete, client, sample_review_data, app):
        app.dependency_overrides[getCurrentUser] = lambda: FakeUser(id=1, username="admin", role="admin")

        mock_get_review.return_value = sample_review_data
        mock_delete.return_value = None

        response = client.delete("/reviews/1")

        assert response.status_code == status.HTTP_204_NO_CONTENT
        mock_delete.assert_called_once_with(1)

        app.dependency_overrides = {}

    @patch('app.routers.reviewRoute.getReviewById')
    def test_delete_review_not_found(self, mock_get_review, client, app):
        app.dependency_overrides[getCurrentUser] = lambda: {"username": "admin", "role": "admin"}
        mock_get_review.return_value = None

        response = client.delete("/reviews/999")

        assert response.status_code == 404
        assert response.json()["detail"] == "Review not found"

        app.dependency_overrides = {}
