import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from app.app import app
from app.routers.auth import getCurrentUser, requireAdmin
from app.schemas.role import Role
from app.schemas.user import User
from app.schemas.review import Review


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
        pw="hashedpassword123",
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
        pw="hashedpassword123",
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


# -----------------------------
# Helper to create mock reviews
# -----------------------------

def createReview(id, movieId, userId, flagged=False):
    return Review(
        id=id,
        movieId=movieId,
        userId=userId,
        reviewTitle="Test Review Title",
        reviewBody="This is a test review body with enough characters.",
        rating=8,
        datePosted="2023-01-01",
        flagged=flagged
    )


def createMockUser(id, penalties=0, isBanned=False):
    return User(
        id=id,
        username=f"user{id}",
        firstName="Test",
        lastName="User",
        age=25,
        email=f"user{id}@test.com",
        pw="hashedpassword",
        role=Role.USER,
        penalties=penalties,
        isBanned=isBanned
    )


# -----------------------------
# Test: GET /admin/reports/reviews - List flagged reviews
# -----------------------------

def test_get_flagged_reviews(client):
    """Test getting paginated flagged reviews"""
    mockReviews = [
        createReview(1, 100, 10, flagged=True),
        createReview(2, 101, 11, flagged=False),
        createReview(3, 102, 12, flagged=True),
        createReview(4, 103, 13, flagged=True),
    ]

    # Patch where loadReviews is used in adminRoute
    with patch("app.routers.adminRoute.loadReviews", return_value=mockReviews):
        response = client.get("/admin/reports/reviews")

    assert response.status_code == 200
    data = response.json()

    assert data["totalFlagged"] == 3
    assert len(data["reviews"]) == 3
    assert data["page"] == 1
    assert data["pageSize"] == 20


def test_get_flagged_reviews_pagination(client):
    """Test pagination of flagged reviews"""
    mockReviews = [createReview(i, 100 + i, 10, flagged=True) for i in range(1, 26)]

    with patch("app.routers.adminRoute.loadReviews", return_value=mockReviews):
        response = client.get("/admin/reports/reviews?page=2&pageSize=10")

    assert response.status_code == 200
    data = response.json()

    assert len(data["reviews"]) == 10
    assert data["page"] == 2
    assert data["pageSize"] == 10
    assert data["totalFlagged"] == 25
    assert data["pageCount"] == 3


def test_get_flagged_reviews_empty(client):
    """Test when there are no flagged reviews"""
    mockReviews = [
        createReview(1, 100, 10, flagged=False),
        createReview(2, 101, 11, flagged=False),
    ]

    with patch("app.routers.adminRoute.loadReviews", return_value=mockReviews):
        response = client.get("/admin/reports/reviews")

    assert response.status_code == 200
    data = response.json()

    assert data["totalFlagged"] == 0
    assert len(data["reviews"]) == 0


# -----------------------------
# Test: POST /admin/reviews/{reviewId}/acceptFlag
# -----------------------------

def test_accept_flag_success(client):
    """Test accepting a flag - should delete review and penalize user"""
    mockReview = createReview(1, 100, 5, flagged=True)
    mockReviews = [mockReview]
    mockUserAfterPenalty = createMockUser(5, penalties=1, isBanned=False)

    with patch("app.routers.adminRoute.loadReviews", return_value=mockReviews), \
         patch("app.routers.adminRoute.deleteReview") as mock_delete, \
         patch("app.routers.adminRoute.incrementPenaltyForUser", return_value=mockUserAfterPenalty) as mock_penalty:
        
        response = client.post("/admin/reviews/1/acceptFlag")

    assert response.status_code == 200
    data = response.json()

    assert data["message"] == "Review flag accepted. Review deleted and user penalized."
    assert data["userId"] == 5
    assert data["penaltyCount"] == 1
    assert data["isBanned"] is False

    # Verify the mocks were called correctly
    mock_delete.assert_called_once_with(1)
    mock_penalty.assert_called_once_with(5)


def test_accept_flag_user_banned(client):
    """Test accepting a flag when user reaches max penalties"""
    mockReview = createReview(1, 100, 5, flagged=True)
    mockReviews = [mockReview]
    mockUserAfterPenalty = createMockUser(5, penalties=3, isBanned=True)

    with patch("app.routers.adminRoute.loadReviews", return_value=mockReviews), \
         patch("app.routers.adminRoute.deleteReview"), \
         patch("app.routers.adminRoute.incrementPenaltyForUser", return_value=mockUserAfterPenalty):
        
        response = client.post("/admin/reviews/1/acceptFlag")

    assert response.status_code == 200
    data = response.json()

    assert data["userId"] == 5
    assert data["penaltyCount"] == 3
    assert data["isBanned"] is True


def test_accept_flag_review_not_found(client):
    """Test accepting flag for non-existent review"""
    with patch("app.routers.adminRoute.loadReviews", return_value=[]):
        response = client.post("/admin/reviews/999/acceptFlag")

    assert response.status_code == 404
    assert "Review not found" in response.json()["detail"]


# -----------------------------
# Test: POST /admin/reviews/{reviewId}/rejectFlag
# -----------------------------

def test_reject_flag_success(client):
    """Test rejecting a flag - should unflag the review"""
    mockReview = createReview(1, 100, 5, flagged=True)
    mockReviews = [mockReview]

    with patch("app.routers.adminRoute.loadReviews", return_value=mockReviews), \
         patch("app.routers.adminRoute.saveReviews") as mock_save:
        
        response = client.post("/admin/reviews/1/rejectFlag")

    assert response.status_code == 200
    data = response.json()

    assert data["message"] == "Flag rejected. Review unflagged (no penalty applied)."
    assert data["userId"] == 5
    assert data["penaltyCount"] == 0
    assert data["isBanned"] is False

    # Verify the review was unflagged
    mock_save.assert_called_once()
    saved_reviews = mock_save.call_args[0][0]
    assert saved_reviews[0].flagged is False


def test_reject_flag_review_not_found(client):
    """Test rejecting flag for non-existent review"""
    with patch("app.routers.adminRoute.loadReviews", return_value=[]):
        response = client.post("/admin/reviews/999/rejectFlag")

    assert response.status_code == 404


# -----------------------------
# Test: POST /admin/reviews/{reviewId}/markInappropriate
# -----------------------------

def test_mark_inappropriate_success(client):
    """Test marking a review as inappropriate"""
    mockReview = createReview(1, 100, 5, flagged=False)
    mockReviews = [mockReview]
    mockUserAfterPenalty = createMockUser(5, penalties=1, isBanned=False)

    with patch("app.routers.adminRoute.loadReviews", return_value=mockReviews), \
         patch("app.routers.adminRoute.saveReviews") as mock_save, \
         patch("app.routers.adminRoute.incrementPenaltyForUser", return_value=mockUserAfterPenalty) as mock_penalty:
        
        response = client.post("/admin/reviews/1/markInappropriate")

    assert response.status_code == 200
    data = response.json()

    assert data["message"] == "Review flagged and user penalized"
    assert data["userId"] == 5
    assert data["penaltyCount"] == 1
    assert data["isBanned"] is False

    # Verify the review was flagged and saved
    mock_save.assert_called_once()
    saved_reviews = mock_save.call_args[0][0]
    assert saved_reviews[0].flagged is True

    # Verify user was penalized
    mock_penalty.assert_called_once_with(5)


def test_mark_inappropriate_review_not_found(client):
    """Test marking non-existent review as inappropriate"""
    with patch("app.routers.adminRoute.loadReviews", return_value=[]):
        response = client.post("/admin/reviews/999/markInappropriate")

    assert response.status_code == 404


# -----------------------------
# Test: Non-Admin Access
# -----------------------------

def test_admin_endpoints_require_admin(client):
    """Test that non-admin users cannot access admin endpoints"""
    def mockGetUserNonAdmin():
        return User(
            id=2,
            username="regular_user",
            firstName="Regular",
            lastName="User",
            age=25,
            email="user@test.com",
            pw="hashedpassword",
            role=Role.USER
        )

    def mockRequireAdminDenied():
        raise HTTPException(status_code=403, detail="Admin access required")

    app.dependency_overrides = {
        getCurrentUser: mockGetUserNonAdmin,
        requireAdmin: mockRequireAdminDenied,
    }

    test_client = TestClient(app)

    # Test all admin endpoints
    endpoints = [
        ("/admin/reports/reviews", "get"),
        ("/admin/reviews/1/acceptFlag", "post"),
        ("/admin/reviews/1/rejectFlag", "post"),
        ("/admin/reviews/1/markInappropriate", "post"),
    ]

    for endpoint, method in endpoints:
        if method == "get":
            response = test_client.get(endpoint)
        else:
            response = test_client.post(endpoint)
        
        assert response.status_code == 403

    app.dependency_overrides = {}