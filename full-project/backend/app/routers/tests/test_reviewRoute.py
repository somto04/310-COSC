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
def sampleReviewData():
    """Sample review data for testing"""
    return Review(
        id=1,
        movieId=1,
        userId=1,
        reviewTitle="Great Movie!",
        reviewBody="This movie was amazing, highly recommend",
        rating=5,
        datePosted="2023-10-01",
        flagged=False,
    )


@pytest.fixture
def sampleReviewsList(sampleReviewData):
    """Sample list of reviews for testing"""
    return [
        sampleReviewData,
        Review(
            id=2,
            movieId=1,
            userId=2,
            reviewTitle="Not bad",
            reviewBody="It was okay, nothing special",
            rating=3,
            datePosted="2023-10-01",
            flagged=False,
        ),
        Review(
            id=3,
            movieId=2,
            userId=1,
            reviewTitle="Disappointed",
            reviewBody="Expected better from this film",
            rating=2,
            datePosted="2023-10-01",
            flagged=False,
        ),
    ]


class FakeUser:
    def __init__(self, id, username, role):
        self.id = id
        self.username = username
        self.role = role


# INTEGRATION TESTS


class TestReviewRouterIntegration:
    """Integration tests for review API endpoints"""

    @patch("app.routers.reviewRoute.listReviews")
    def test_getAllReviewsEndpoint(self, mockList, client, sampleReviewsList):
        mockList.return_value = sampleReviewsList

        response = client.get("/reviews")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert data[0]["reviewTitle"] == "Great Movie!"
        assert data[1]["reviewTitle"] == "Not bad"

    @patch("app.routers.reviewRoute.getReviewById")
    def test_getReviewByIdEndpoint(self, mockGet, client, sampleReviewData):
        mockGet.return_value = sampleReviewData

        response = client.get("/reviews/1")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["reviewTitle"] == "Great Movie!"
        assert data["rating"] == 5
        mockGet.assert_called_once_with(1)

    @patch("app.routers.reviewRoute.getReviewById")
    def test_getReviewByIdNotFound(self, mockGet, client):
        mockGet.side_effect = HTTPException(status_code=404, detail="Review not found")

        response = client.get("/reviews/999")

        assert response.status_code == 404
        assert response.json()["detail"] == "Review not found"

    @patch("app.routers.reviewRoute.searchReviews")
    def test_searchReviewsWithQuery(self, mockSearch, client, sampleReviewData):
        mockSearch.return_value = [sampleReviewData]

        response = client.get("/reviews/search", params={"query": "great"})
        mockSearch.assert_called_once_with("great")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["reviewTitle"] == "Great Movie!"
        mockSearch.assert_called_once_with("great")

    @patch("app.routers.reviewRoute.searchReviews")
    def test_searchReviewsWithLimitAndOffset(
        self, mockSearch, client, sampleReviewsList
    ):
        mockSearch.return_value = sampleReviewsList

        response = client.get("/reviews/search?query=movie&limit=2&offset=1")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["id"] == 2  # now int, not str

    @patch("app.routers.reviewRoute.createReview")
    def test_createReviewEndpoint(self, mockCreate, client, sampleReviewData, app):
        """Test POST /reviews creates a new review"""
        # Arrange
        mockCreate.return_value = sampleReviewData

        newReview = ReviewCreate(
            reviewTitle="Great Movie!",
            reviewBody="This movie was amazing, highly recommend",
            rating=5,
        )

        app.dependency_overrides[getCurrentUser] = lambda: FakeUser(
            id=1, username="testuser", role="user"
        )

        # Send request with auth header
        response = client.post(
            "/reviews/1",
            json=newReview.model_dump(),
            headers={"Authorization": "Bearer testuser"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["reviewTitle"] == "Great Movie!"
        assert data["rating"] == 5

    @patch("app.routers.reviewRoute.updateReview")
    @patch("app.routers.reviewRoute.getReviewById")
    def test_updateReviewEndpoint(
        self, mockGetReview, mockUpdate, client, sampleReviewData, app
    ):
        """Test PUT /reviews/{id} updates a review.
        It verifies that the FastAPI route for updating a review correctly
        updates an existing review's data and returns the modified view.
        """
        # Arrange
        # Mock getting the existing review (for ownership check)
        mockGetReview.return_value = sampleReviewData

        # Set up expected updated review
        updatedReview = sampleReviewData.model_copy()
        updatedReview.reviewBody = "Updated review text"
        updatedReview.rating = 4
        mockUpdate.return_value = updatedReview

        updateData = ReviewUpdate(reviewBody="Updated review text", rating=4)

        app.dependency_overrides[getCurrentUser] = lambda: FakeUser(
            id=1,
            username="testuser",
            role="user",
        )

        response = client.put(
            "/reviews/1",
            json=updateData.model_dump(),
            headers={"Authorization": "Bearer testuser"},
        )

        # Assert
        app.dependency_overrides = {}

        assert response.status_code == 200
        data = response.json()
        assert data["reviewBody"] == "Updated review text"
        assert data["rating"] == 4

    @patch("app.routers.reviewRoute.deleteReview")
    @patch("app.routers.reviewRoute.getReviewById")
    def test_deleteReviewAsAdmin(
        self, mockGetReview, mockDelete, client, sampleReviewData, app
    ):
        app.dependency_overrides[getCurrentUser] = lambda: FakeUser(
            id=1, username="admin", role="admin"
        )

        mockGetReview.return_value = sampleReviewData
        mockDelete.return_value = None

        response = client.delete("/reviews/1")

        assert response.status_code == status.HTTP_204_NO_CONTENT
        mockDelete.assert_called_once_with(1)

        app.dependency_overrides = {}

    @patch("app.routers.reviewRoute.getReviewById")
    def test_deleteReviewNotFound(self, mockGetReview, client, app):
        app.dependency_overrides[getCurrentUser] = lambda: {
            "username": "admin",
            "role": "admin",
        }
        mockGetReview.return_value = None

        response = client.delete("/reviews/999")

        assert response.status_code == 404
        assert response.json()["detail"] == "Review not found"

        app.dependency_overrides = {}
