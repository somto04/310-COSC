import pytest
from fastapi.testclient import TestClient
from app.app import app
from app.schemas.review import Review
from app.schemas.user import User
from app.schemas.role import Role
from app.repos.reviewRepo import saveReviews
from app.repos.userRepo import saveUsers, loadUsers
from app.routers import adminRoute

client = TestClient(app)

# -----------------------------------
# Helper setup functions
# -----------------------------------

def setup_review(review_id=1, flagged=True, user_id=10):
    """Create one mock review using Pydantic Review model."""
    review = Review(
        id=review_id,
        movieId=1,
        userId=user_id,
        reviewTitle="Test",
        reviewBody="Body",
        rating=8,
        flagged=flagged
    )
    saveReviews([review])
    return review

def setup_user(user_id=10, penalties=0, isBanned=False, role=Role.USER):
    """Create one mock user using Pydantic User model."""
    user = User(
        id=user_id,
        username="testUser",
        firstName="Test",
        lastName="User",
        age=25,
        email="testuser@example.com",
        pw="H@shed123",
        role=role,
        penalties=penalties,
        isBanned=isBanned
    )
    saveUsers([user])
    return user

# -----------------------------------
# Override admin dependency
# -----------------------------------

def fake_admin_dep():
    return User(
        id=999,
        username="admin",
        firstName="Admin",
        lastName="User",
        age=30,
        email="admin@example.com",
        pw="Admin123",
        role=Role.ADMIN,
        penalties=0,
        isBanned=False
    )

# Apply the dependency override
app.dependency_overrides[adminRoute.requireAdmin] = fake_admin_dep

# -----------------------------------
# Tests
# -----------------------------------

def test_accept_flag_penalizes_user():
    setup_review(review_id=1, flagged=True, user_id=10)
    setup_user(user_id=10, penalties=0)

    response = client.post("/admin/reviews/1/acceptFlag")
    assert response.status_code == 200

    data = response.json()
    assert data["penaltyCount"] == 1
    assert data["isBanned"] is False

def test_reject_flag_does_not_penalize():
    setup_review(review_id=2, flagged=True, user_id=10)
    setup_user(user_id=10, penalties=0)

    response = client.post("/admin/reviews/2/rejectFlag")
    assert response.status_code == 200

    user = loadUsers()[0]
    assert user.penalties == 0

def test_mark_inappropriate_flags_and_penalizes():
    setup_review(review_id=3, flagged=False, user_id=10)
    setup_user(user_id=10, penalties=1)

    response = client.post("/admin/reviews/3/markInappropriate")
    assert response.status_code == 200

    data = response.json()
    assert data["penaltyCount"] == 2
    assert data["isBanned"] is False

def test_get_flagged_reviews_pagination():
    setup_review(review_id=5, flagged=True, user_id=10)
    setup_user(user_id=10)

    response = client.get("/admin/reports/reviews?page=1&pageSize=10")
    assert response.status_code == 200

    data = response.json()
    assert data["totalFlagged"] >= 1
    assert len(data["reviews"]) >= 1
    assert data["page"] == 1

def test_nonexistent_review_returns_404():
    # Clear all reviews
    saveReviews([])

    response = client.post("/admin/reviews/999/acceptFlag")
    assert response.status_code == 404
