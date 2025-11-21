from fastapi import APIRouter, Depends, HTTPException
from .auth import requireAdmin
from ..repos.reviewRepo import loadReviews, saveReviews
from ..utilities.penalties import incrementPenaltyForUser
from .reviewRoute import validateReview
from ..schemas.user import CurrentUser

router = APIRouter(prefix="/admin", tags=["admin"])


def getReviewById(reviewId: int):
    """Return list of reviews and the one matching the ID."""
    reviewList = loadReviews()
    review = next((review for review in reviewList if review.id == reviewId), None)
    if review is None:
        raise HTTPException(404, "Review not found")
    return reviewList, review


@router.post("/reviews/{reviewId}/acceptFlag")
def acceptReviewFlag(reviewId: int, currentAdmin: CurrentUser = Depends(requireAdmin)):
    reviewList, review = getReviewById(reviewId)
    validateReview(review)

    review.flagged = False
    updatedUser = incrementPenaltyForUser(review.userId)
    saveReviews(reviewList)

    return {
        "message": "Review flag accepted and cleared",
        "userId": updatedUser.id,
        "penaltyCount": updatedUser.penalties,
        "isBanned": updatedUser.isBanned,
    }


@router.post("/reviews/{reviewId}/rejectFlag")
def rejectReviewFlag(reviewId: int, currentAdmin: CurrentUser = Depends(requireAdmin)):
    reviewList, review = getReviewById(reviewId)
    validateReview(review)

    review.flagged = False
    saveReviews(reviewList)

    return {
        "message": "Flag rejected. Review unflagged (no penalty applied).",
        "reviewId": reviewId
    }


@router.post("/reviews/{reviewId}/markInappropriate")
def markReviewInappropriate(reviewId: int, currentAdmin: CurrentUser = Depends(requireAdmin)):
    reviewList, review = getReviewById(reviewId)
    validateReview(review)

    review.flagged = True
    saveReviews(reviewList)

    updatedUser = incrementPenaltyForUser(review.userId)

    return {
        "message": "Review flagged and user penalized",
        "userId": updatedUser.id,
        "penaltyCount": updatedUser.penalties,
        "isBanned": updatedUser.isBanned,
    }


def getFlaggedReviews():
    reviewList = loadReviews()
    return [review for review in reviewList if review.flagged is True]


@router.get("/reports/reviews")
def getFlaggedReviewReports(
    page: int = 1,
    pageSize: int = 20,
    currentAdmin: CurrentUser = Depends(requireAdmin),):
    flaggedReviewList = getFlaggedReviews()

    startIndex = (page - 1) * pageSize
    endIndex = startIndex + pageSize
    paginatedReviews = flaggedReviewList[startIndex:endIndex]

    return {
        "page": page,
        "pageSize": pageSize,
        "totalFlagged": len(flaggedReviewList),
        "pageCount": (len(flaggedReviewList) + pageSize - 1) // pageSize,
        "reviews": paginatedReviews,
    }