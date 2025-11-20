import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from fastapi import FastAPI, HTTPException
# Import router
from app.routers.adminRoute import router as adminRouter


# Test Application Setup
@pytest.fixture
def testApp():
    app = FastAPI()
    app.include_router(adminRouter)
    return app


@pytest.fixture
def client(testApp):
    return TestClient(testApp)


# Helpers for Fake Data
class FakeReview:
    def __init__(self, reviewId, userId, flagged=False, flagCount=1):
        self.Id = reviewId
        self.userId = userId
        self.flagged = flagged
        self.flagCount = flagCount


class FakeUser:
    def __init__(self, userId, penalties=0, isBanned=False):
        self.id = userId
        self.penalties = penalties
        self.isBanned = isBanned


# Mock requireAdmin
def mockRequireAdmin():
    """Pretend the user is always an admin."""
    return {"role": "admin", "username": "testadmin", "isBanned": False}


# TEST: acceptReviewFlag
@patch("app.routers.adminRoute.saveReviews")
@patch("app.routers.adminRoute.incrementPenaltyForUser")
@patch("app.routers.adminRoute.validateReview")
@patch("app.routers.adminRoute.loadReviews")
@patch("app.routers.adminRoute.requireAdmin", new=mockRequireAdmin)
def test_accept_flag(
    mockLoadReviews,
    mockValidate,
    mockIncrementPenalty,
    mockSave,
    client
):
    fakeReview = FakeReview(reviewId=10, userId=300, flagged=True)
    fakeUser = FakeUser(userId=300, penalties=1)

    mockLoadReviews.return_value = [fakeReview]
    mockIncrementPenalty.return_value = fakeUser

    response = client.post("/admin/reviews/10/acceptFlag")
    result = response.json()

    assert response.status_code == 200
    assert result["message"] == "Review flag accepted and cleared"
    assert fakeReview.flagged is False
    assert result["penaltyCount"] == 1
    mockSave.assert_called_once()


# TEST: rejectReviewFlag
@patch("app.routers.adminRoute.saveReviews")
@patch("app.routers.adminRoute.validateReview")
@patch("app.routers.adminRoute.loadReviews")
@patch("app.routers.adminRoute.requireAdmin", new=mockRequireAdmin)
def test_reject_flag(
    mockLoadReviews,
    mockValidate,
    mockSave,
    client
):
    fakeReview = FakeReview(reviewId=7, userId=123, flagged=True)
    mockLoadReviews.return_value = [fakeReview]

    response = client.post("/admin/reviews/7/rejectFlag")
    result = response.json()

    assert response.status_code == 200
    assert result["message"].startswith("Flag rejected")
    assert fakeReview.flagged is False
    mockSave.assert_called_once()


# TEST: markReviewInappropriate
@patch("app.routers.adminRoute.saveReviews")
@patch("app.routers.adminRoute.incrementPenaltyForUser")
@patch("app.routers.adminRoute.validateReview")
@patch("app.routers.adminRoute.loadReviews")
@patch("app.routers.adminRoute.requireAdmin", new=mockRequireAdmin)
def test_mark_inappropriate(
    mockLoadReviews,
    mockValidate,
    mockIncrementPenalty,
    mockSave,
    client
):
    fakeReview = FakeReview(reviewId=5, userId=200, flagged=False)
    fakeUser = FakeUser(userId=200, penalties=2)

    mockLoadReviews.return_value = [fakeReview]
    mockIncrementPenalty.return_value = fakeUser

    response = client.post("/admin/reviews/5/markInappropriate")
    result = response.json()

    assert response.status_code == 200
    assert fakeReview.flagged is True
    assert result["penaltyCount"] == 2
    mockSave.assert_called_once()


# TEST: getFlaggedReviewReports (pagination, sorting, filtering)
@patch("app.routers.adminRoute.requireAdmin", new=mockRequireAdmin)
@patch("app.routers.adminRoute.getFlaggedReviews")
def test_paginated_sorted_filtered_reviews(mockGetFlagged, client):
    # fake reviews with different flag counts
    reviews = [
        FakeReview(1, 10, flagged=True, flagCount=5),
        FakeReview(2, 20, flagged=True, flagCount=3),
        FakeReview(3, 30, flagged=True, flagCount=10),
    ]
    mockGetFlagged.return_value = reviews

    response = client.get(
        "/admin/reports/reviews?page=1&pageSize=2&sortBy=mostFlagged&minFlags=4"
    )
    data = response.json()

    assert response.status_code == 200
    assert data["page"] == 1
    assert data["pageSize"] == 2

    # after filtering by minFlags=4, reviews with flagCount >= 4 remain:
    # review 3, review 1 (flagCount 10 and 5)
    assert len(data["reviews"]) == 2
    assert data["reviews"][0]["Id"] == 3  # highest flagCount first
    assert data["reviews"][1]["Id"] == 1


# TEST: Unauthorized access (requireAdmin)
def mockRequireAdminFail():
    raise HTTPException(status_code=403, detail="Admin only")


@patch("app.routers.adminRoute.requireAdmin", new=mockRequireAdminFail)
def test_admin_protection(client):
    response = client.get("/admin/reports/reviews")
    assert response.status_code == 403
