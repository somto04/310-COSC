import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from fastapi import HTTPException

from app.app import app
from app.routers.auth import getCurrentUser, requireAdmin
from app.schemas.role import Role
from app.schemas.user import User
from app.schemas.review import Review
import app.repos.reviewRepo as reviewRepo


@pytest.fixture(autouse=True)
def isolateReviewJsonForAdminTests(tmp_path, monkeypatch):
    tempFile = tmp_path / "reviews_admin.json"
    monkeypatch.setattr(reviewRepo, "REVIEW_DATA_PATH", tempFile, raising=False)
    reviewRepo._REVIEW_CACHE = None
    reviewRepo._NEXT_REVIEW_ID = None
    if not tempFile.exists():
        tempFile.write_text("[]", encoding="utf-8")


def mockGetCurrentUser():
    return User(
        id=1,
        username="admin",
        firstName="Admin",
        lastName="User",
        age=30,
        email="admin@test.com",
        pw="hashedpassword123",
        role=Role.ADMIN,
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
        role=Role.ADMIN,
    )


@pytest.fixture
def client():
    app.dependency_overrides = {
        getCurrentUser: mockGetCurrentUser,
        requireAdmin: mockRequireAdmin,
    }

    testClient = TestClient(app)
    yield testClient

    app.dependency_overrides = {}


def createReview(id, movieId, userId, flagged=False):
    return Review(
        id=id,
        movieId=movieId,
        userId=userId,
        reviewTitle="Test Review Title",
        reviewBody="This is a test review body with enough characters.",
        rating=8,
        datePosted="2023-01-01",
        flagged=flagged,
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
        isBanned=isBanned,
    )


def test_get_flagged_reviews(client):
    mockReviews = [
        createReview(1, 100, 10, flagged=True),
        createReview(2, 101, 11, flagged=False),
        createReview(3, 102, 12, flagged=True),
        createReview(4, 103, 13, flagged=True),
    ]

    with patch("app.routers.adminRoute.loadReviews", return_value=mockReviews):
        response = client.get("/admin/reports/reviews")

    assert response.status_code == 200
    data = response.json()

    assert data["totalFlagged"] == 3
    assert len(data["reviews"]) == 3
    assert data["page"] == 1
    assert data["pageSize"] == 20


def test_get_flagged_reviews_pagination(client):
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


def test_accept_flag_success(client):
    mockReview = createReview(1, 100, 5, flagged=True)
    mockReviews = [mockReview]
    mockUserAfterPenalty = createMockUser(5, penalties=1, isBanned=False)

    with patch("app.routers.adminRoute.loadReviews", return_value=mockReviews), \
         patch("app.routers.adminRoute.deleteReview") as mockDelete, \
         patch("app.routers.adminRoute.incrementPenaltyForUser", return_value=mockUserAfterPenalty) as mockPenalty:

        response = client.post("/admin/reviews/1/acceptFlag")

    assert response.status_code == 200
    data = response.json()

    assert data["message"] == "Review flag accepted. Review deleted and user penalized."
    assert data["userId"] == 5
    assert data["penaltyCount"] == 1
    assert data["isBanned"] is False

    mockDelete.assert_called_once_with(1)
    mockPenalty.assert_called_once_with(5)


def test_accept_flag_user_banned(client):
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
    with patch("app.routers.adminRoute.loadReviews", return_value=[]):
        response = client.post("/admin/reviews/999/acceptFlag")

    assert response.status_code == 404
    assert "Review not found" in response.json()["detail"]


def test_reject_flag_success(client):
    mockReview = createReview(1, 100, 5, flagged=True)
    mockReviews = [mockReview]

    with patch("app.routers.adminRoute.loadReviews", return_value=mockReviews), \
         patch("app.routers.adminRoute.saveReviews") as mockSave:

        response = client.post("/admin/reviews/1/rejectFlag")

    assert response.status_code == 200
    data = response.json()

    assert data["message"] == "Flag rejected. Review unflagged (no penalty applied)."
    assert data["userId"] == 5
    assert data["penaltyCount"] == 0
    assert data["isBanned"] is False

    mockSave.assert_called_once()
    savedReviews = mockSave.call_args[0][0]
    assert savedReviews[0].flagged is False


def test_reject_flag_review_not_found(client):
    with patch("app.routers.adminRoute.loadReviews", return_value=[]):
        response = client.post("/admin/reviews/999/rejectFlag")

    assert response.status_code == 404


def test_mark_inappropriate_success(client):
    mockReview = createReview(1, 100, 5, flagged=False)
    mockReviews = [mockReview]
    mockUserAfterPenalty = createMockUser(5, penalties=1, isBanned=False)

    with patch("app.routers.adminRoute.loadReviews", return_value=mockReviews), \
         patch("app.routers.adminRoute.saveReviews") as mockSave, \
         patch("app.routers.adminRoute.incrementPenaltyForUser", return_value=mockUserAfterPenalty) as mockPenalty, \
         patch("app.routers.adminRoute.deleteReview") as mockDelete:

        response = client.post("/admin/reviews/1/markInappropriate")

    assert response.status_code == 200
    data = response.json()

    assert data["message"] == "Review flagged and user penalized"
    assert data["userId"] == 5
    assert data["penaltyCount"] == 1
    assert data["isBanned"] is False

    mockSave.assert_called_once()
    savedReviews = mockSave.call_args[0][0]
    assert savedReviews[0].flagged is True

    mockPenalty.assert_called_once_with(5)
    mockDelete.assert_called_once_with(1)



def test_mark_inappropriate_review_not_found(client):
    with patch("app.routers.adminRoute.loadReviews", return_value=[]):
        response = client.post("/admin/reviews/999/markInappropriate")

    assert response.status_code == 404


def test_admin_endpoints_require_admin(client):
    def mockGetUserNonAdmin():
        return User(
            id=2,
            username="regular_user",
            firstName="Regular",
            lastName="User",
            age=25,
            email="user@test.com",
            pw="hashedpassword",
            role=Role.USER,
        )

    def mockRequireAdminDenied():
        raise HTTPException(status_code=403, detail="Admin access required")

    app.dependency_overrides = {
        getCurrentUser: mockGetUserNonAdmin,
        requireAdmin: mockRequireAdminDenied,
    }

    testClient = TestClient(app)

    endpoints = [
        ("/admin/reports/reviews", "get"),
        ("/admin/reviews/1/acceptFlag", "post"),
        ("/admin/reviews/1/rejectFlag", "post"),
        ("/admin/reviews/1/markInappropriate", "post"),
    ]

    for endpoint, method in endpoints:
        if method == "get":
            response = testClient.get(endpoint)
        else:
            response = testClient.post(endpoint)

        assert response.status_code == 403

    app.dependency_overrides = {}
