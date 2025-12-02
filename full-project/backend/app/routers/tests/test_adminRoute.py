import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from fastapi import HTTPException

from app.app import app
from app.routers.authRoute import getCurrentUser, requireAdmin
from app.schemas.role import Role
from app.schemas.user import User
from app.schemas.review import Review
import app.repos.reviewRepo as reviewRepo
from app.services.adminService import AdminActionError
from app.services.userService import UserNotFoundError
from app.services.reviewService import ReviewNotFoundError
from unittest.mock import ANY


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


def createMockUser(id, penalties=0, isBanned=False, role=Role.USER):
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


def test_accept_flag_success(client):
    mockReview = createReview(1, 100, 5, flagged=True)
    mockUserAfterPenalty = createMockUser(5, penalties=3, isBanned=True)

    with patch(
        "app.routers.adminRoute.getReviewById", return_value=mockReview
    ) as mockGet, patch(
        "app.routers.adminRoute.incrementPenaltyForUser",
        return_value=mockUserAfterPenalty,
    ) as mockPenalty, patch(
        "app.routers.adminRoute.deleteReview"
    ) as mockDelete:

        response = client.post("/admin/reviews/1/acceptFlag")

    assert response.status_code == 200
    data = response.json()

    assert data["message"] == "Review flag accepted. Review deleted and user penalized."
    assert data["userId"] == 5
    assert data["penaltyCount"] == 3
    assert data["isBanned"] is True

    mockGet.assert_called_once_with(1)
    mockPenalty.assert_called_once_with(5)
    mockDelete.assert_called_once_with(1)


def test_accept_flag_review_not_flagged_returns_400(client):
    mockReview = createReview(1, 100, 5, flagged=False)

    with patch("app.routers.adminRoute.getReviewById", return_value=mockReview):
        response = client.post("/admin/reviews/1/acceptFlag")

    assert response.status_code == 400
    body = response.json()
    assert body["detail"] == "Cannot accept flag. Review is not flagged."


def test_accept_flag_review_not_found_returns_404(client):
    with patch(
        "app.routers.adminRoute.getReviewById",
        side_effect=ReviewNotFoundError("Review not found"),
    ):
        response = client.post("/admin/reviews/999/acceptFlag")

    assert response.status_code == 404
    body = response.json()
    assert body["detail"] == "Review not found"


def test_reject_flag_success(client):
    mockReview = createReview(1, 100, 5, flagged=True)
    mockUpdated = createReview(1, 100, 5, flagged=False)

    with patch(
        "app.routers.adminRoute.getReviewById",
        return_value=mockReview,
    ) as mockGet, patch(
        "app.routers.adminRoute.unflagReview",
        return_value=mockUpdated,
    ) as mockUnflag:

        res = client.post("/admin/reviews/1/rejectFlag")

    assert res.status_code == 200
    data = res.json()

    assert data["message"] == "Flag rejected. Review unflagged (no penalty applied)."
    assert data["userId"] == 5
    assert data["penaltyCount"] == 0
    assert data["isBanned"] is False

    mockGet.assert_called_once_with(1)
    mockUnflag.assert_called_once_with(1)


def test_reject_flag_not_flagged_returns_400(client):
    mockReview = createReview(1, 100, 5, flagged=False)

    with patch(
        "app.routers.adminRoute.getReviewById",
        return_value=mockReview,
    ):
        res = client.post("/admin/reviews/1/rejectFlag")

    assert res.status_code == 400
    assert res.json()["detail"] == "Cannot reject flag. Review is not flagged."


def test_reject_flag_review_not_found_returns_404(client):
    with patch(
        "app.routers.adminRoute.getReviewById",
        side_effect=ReviewNotFoundError("Review not found"),
    ):
        res = client.post("/admin/reviews/999/rejectFlag")

    assert res.status_code == 404
    assert res.json()["detail"] == "Review not found"


def test_get_flagged_review_reports_default_pagination(client):
    # 3 flagged, 1 not flagged just to prove the helper filters
    reviews = [
        createReview(1, 101, 11, flagged=True),
        createReview(2, 102, 12, flagged=False),
        createReview(3, 103, 13, flagged=True),
        createReview(4, 104, 14, flagged=True),
    ]

    # getFlaggedReviews should already do the filtering, so we mock it directly
    with patch("app.routers.adminRoute.getFlaggedReviews", return_value=reviews):
        response = client.get("/admin/reports/reviews")

    assert response.status_code == 200
    data = response.json()

    assert data["page"] == 1
    assert data["pageSize"] == 20
    assert data["totalFlagged"] == 4
    assert data["pageCount"] == 1
    assert len(data["reviews"]) == 4
    # sanity: first item is what we expect
    assert data["reviews"][0]["id"] == 1


def test_get_flagged_review_reports_custom_page_and_size(client):
    # 25 flagged reviews so we can actually paginate
    reviews = [createReview(i, 100 + i, 10 + i, flagged=True) for i in range(1, 26)]

    with patch("app.routers.adminRoute.getFlaggedReviews", return_value=reviews):
        response = client.get("/admin/reports/reviews?page=2&pageSize=10")

    assert response.status_code == 200
    data = response.json()

    # second page of 10 out of 25
    assert data["page"] == 2
    assert data["pageSize"] == 10
    assert data["totalFlagged"] == 25
    # ceil(25 / 10) = 3
    assert data["pageCount"] == 3
    assert len(data["reviews"]) == 10
    # first review on page 2 should be index 10 in the original list -> id 11
    assert data["reviews"][0]["id"] == 11


def test_get_flagged_review_reports_empty(client):
    with patch("app.routers.adminRoute.getFlaggedReviews", return_value=[]):
        response = client.get("/admin/reports/reviews")

    assert response.status_code == 200
    data = response.json()

    assert data["page"] == 1
    assert data["pageSize"] == 20
    assert data["totalFlagged"] == 0
    assert data["pageCount"] == 0
    assert data["reviews"] == []


# ---------------------------
# ADMIN ROLE MANAGEMENT TESTS
# ---------------------------


def createMockAdminUser(id=1):
    return User(
        id=id,
        username=f"admin{id}",
        firstName="Admin",
        lastName="User",
        age=30,
        email=f"admin{id}@test.com",
        pw="hashedpw",
        role=Role.ADMIN,
        penalties=0,
        isBanned=False,
    )


def createMockRegularUser(id=2):
    return User(
        id=id,
        username=f"user{id}",
        firstName="Test",
        lastName="User",
        age=25,
        email=f"user{id}@test.com",
        pw="hashedpw",
        role=Role.USER,
        penalties=0,
        isBanned=False,
    )


def test_grant_admin_success(client):
    updatedUser = createMockAdminUser(id=5)

    with patch("app.routers.adminRoute.grantAdmin", return_value=updatedUser):
        response = client.put("/admin/5/grantAdmin")

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Admin privileges granted."
    assert data["userId"] == 5
    assert data["role"] == Role.ADMIN


def test_revoke_admin_success(client):
    updatedUser = createMockRegularUser(id=5)

    with patch("app.routers.adminRoute.revokeAdmin", return_value=updatedUser):
        response = client.put("/admin/5/revokeAdmin")

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Admin privileges revoked."
    assert data["userId"] == 5
    assert data["role"] == Role.USER


def test_grant_admin_action_error(client):
    with patch(
        "app.routers.adminRoute.grantAdmin",
        side_effect=AdminActionError("nope"),
    ):
        response = client.put("/admin/5/grantAdmin")

    assert response.status_code == 400
    assert response.json()["detail"] == "nope"


def test_revoke_admin_action_error(client):
    with patch(
        "app.routers.adminRoute.revokeAdmin",
        side_effect=AdminActionError("cannot"),
    ):
        response = client.put("/admin/5/revokeAdmin")

    assert response.status_code == 400
    assert response.json()["detail"] == "cannot"


def test_grant_admin_user_not_found(client):
    with patch(
        "app.routers.adminRoute.grantAdmin",
        side_effect=UserNotFoundError("not found"),
    ):
        response = client.put("/admin/999/grantAdmin")

    assert response.status_code == 404
    assert response.json()["detail"] == "not found"


def test_revoke_admin_user_not_found(client):
    with patch(
        "app.routers.adminRoute.revokeAdmin",
        side_effect=UserNotFoundError("missing"),
    ):
        response = client.put("/admin/999/revokeAdmin")

    assert response.status_code == 404
    assert response.json()["detail"] == "missing"


def test_admin_role_endpoints_require_admin(client):
    def mockFailsRequireAdmin():
        raise HTTPException(status_code=403, detail="Admin access required")

    app.dependency_overrides[requireAdmin] = mockFailsRequireAdmin
    testClient = TestClient(app)

    endpoints = [
        "/admin/5/grantAdmin",
        "/admin/5/revokeAdmin",
    ]

    for ep in endpoints:
        response = testClient.put(ep)
        assert response.status_code == 403

    app.dependency_overrides = {}