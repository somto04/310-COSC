import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, PropertyMock
from fastapi import HTTPException
from app.app import app
from app.routers.auth import getCurrentUser, requireAdmin
from app.schemas.role import Role
from app.schemas.user import User

# -----------------------------
# Mock Users for Admin Access
# -----------------------------

def mockGetCurrentUser():
    return User(
        id=1, 
        username="admin", 
        firstName="Admin",
        lastName="User",
        age=30,
        email="admin@test.com",
        pw="hashedPassword123",
        role=Role.ADMIN
    )


def mockRequireAdmin():
    return User(
        id=1, 
        username="admin", 
        firstName="Admin",
        lastName="User",
        age=30,
        email="admin@test.com",
        pw="hashedPassword1234",
        role=Role.ADMIN
    )


@pytest.fixture
def client():
    app.dependency_overrides = {
        getCurrentUser: mockGetCurrentUser,
        requireAdmin: mockRequireAdmin,
    }

    test_client = TestClient(app)
    yield test_client

    app.dependency_overrides = {}


# Helper function to create a simple object (not MagicMock)
class MockReview:
    def __init__(self, id, flagged, createdAt="2023-01-01", flagCount=1):
        self.id = id
        self.Id = id  # Your code uses review.Id in getReviewById
        self.flagged = flagged
        self.createdAt = createdAt
        self.flagCount = flagCount


# -----------------------------
# Test: GET /admin/reports/reviews
# -----------------------------
def test_get_flagged_reviews(client):
    mockReviews = [
        MockReview(1, True, "2023-01-01"),
        MockReview(2, False, "2023-01-02"),
        MockReview(3, True, "2023-01-03"),
    ]

    with patch("app.repos.reviewRepo.loadReviews", return_value=mockReviews):
        response = client.get("/admin/reports/reviews")

    assert response.status_code == 200
    data = response.json()

    # Check the reviews array in the response
    assert len(data["reviews"]) == 2
    assert data["totalFlagged"] == 2


# -----------------------------
# Test: Pagination
# -----------------------------
def test_get_flagged_reviews_pagination(client):
    mockReviews = [MockReview(i, True, "2023-01-01") for i in range(1, 21)]

    with patch("app.repos.reviewRepo.loadReviews", return_value=mockReviews):
        response = client.get("/admin/reports/reviews?page=2&pageSize=5")

    assert response.status_code == 200
    data = response.json()

    assert len(data["reviews"]) == 5
    assert data["page"] == 2
    assert data["pageSize"] == 5


# -----------------------------
# Test: Sorting by Most Flagged
# -----------------------------
def test_get_flagged_reviews_sorting(client):
    mockReviews = [
        MockReview(1, True, "2023-01-01", flagCount=3),
        MockReview(2, True, "2023-01-02", flagCount=10),
        MockReview(3, True, "2023-01-03", flagCount=1),
    ]

    with patch("app.repos.reviewRepo.loadReviews", return_value=mockReviews):
        response = client.get("/admin/reports/reviews?sortBy=mostFlagged")

    assert response.status_code == 200
    data = response.json()

    # The response contains the actual review objects, access their attributes
    reviews = data["reviews"]
    assert len(reviews) == 3
    
    # Check if sorted by flagCount descending
    assert reviews[0].id == 2  # flagCount=10
    assert reviews[1].id == 1  # flagCount=3
    assert reviews[2].id == 3  # flagCount=1


# -----------------------------
# Test: Non-Admin Access
# -----------------------------
def test_get_flagged_non_admin_denied():
    def mockGetUserNonAdmin():
        return User(
            id=2, 
            username="bob", 
            firstName="Bob",
            lastName="Smith",
            age=25,
            email="bob@test.com",
            pw="hashedPassword125",
            role=Role.USER
        )

    def mockRequireAdminDenied():
        raise HTTPException(status_code=403, detail="Admin only")

    app.dependency_overrides = {
        getCurrentUser: mockGetUserNonAdmin,
        requireAdmin: mockRequireAdminDenied,
    }

    test_client = TestClient(app)
    response = test_client.get("/admin/reports/reviews")

    assert response.status_code == 403

    app.dependency_overrides = {}


# -----------------------------
# Test: No Flagged Reviews
# -----------------------------
def test_no_flagged_reviews(client):
    mockReviews = [
        MockReview(1, False),
        MockReview(2, False),
    ]

    with patch("app.repos.reviewRepo.loadReviews", return_value=mockReviews):
        response = client.get("/admin/reports/reviews")

    assert response.status_code == 200
    data = response.json()
    assert data["reviews"] == []
    assert data["totalFlagged"] == 0