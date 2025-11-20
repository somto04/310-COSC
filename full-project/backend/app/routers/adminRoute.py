from fastapi import APIRouter, Depends, HTTPException, status
from auth import requireAdmin
from ..repos.reviewRepo import loadReviews, saveReviews
from ..utilities.penalties import incrementPenaltyForUser
from .reviewRoute import validateReview
from ..schemas.user import CurrentUser

router = APIRouter(prefix="/admin", tags=["admin"])


# Proper helper: returns BOTH review list and review object
def getReviewById(reviewId: int):
    reviewList = loadReviews()
    review = next((review for review in reviewList if review.Id == reviewId), None)
    return reviewList, review


@router.post("/reviews/{reviewId}/acceptFlag")
def acceptReviewFlag(reviewId: int, currentAdmin: CurrentUser = Depends(requireAdmin)):
    """
    Admin accepts the flag.
    -> penalize user
    -> unflag review
    """
    reviewList, review = getReviewById(reviewId)
    validateReview(review)

    review.flagged = False

    updatedUser = incrementPenaltyForUser(int(review.userId))
    saveReviews(reviewList)

    return {
        "message": "Review flag accepted and cleared",
        "userId": updatedUser.id,
        "penaltyCount": updatedUser.penalties,
        "isBanned": updatedUser.isBanned,
    }


@router.post("/reviews/{reviewId}/rejectFlag")
def rejectReviewFlag(reviewId: int, currentAdmin: CurrentUser = Depends(requireAdmin)):
    """
    Admin rejects the flag.
    -> no penalty
    -> unflag review
    """
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

    updatedUser = incrementPenaltyForUser(int(review.userId))

    return {
        "message": "Review flagged and user penalized",
        "userId": updatedUser.id,
        "penaltyCount": updatedUser.penalties,
        "isBanned": updatedUser.isBanned,
    }


def getFlaggedReviews():
    """ Internal helper to get all flagged reviews """
    reviewList = loadReviews()
    return [review for review in reviewList if review.flagged is True]


@router.get("/reports/reviews")
def getFlaggedReviewReports(
    page: int = 1,
    pageSize: int = 20,
    sortBy: str = "mostFlagged",
    minFlags: int = 0,
    currentAdmin: CurrentUser = Depends(requireAdmin),
):
    """
    Admin endpoint - return flagged review reports.
    Supports:
      - Pagination (20 per page)
      - Sorting ("mostFlagged")
      - Filtering by minimum flag count
    """

    flaggedReviewList = getFlaggedReviews()

    # Filtering by minimum flag count
    if minFlags > 0:
        flaggedReviewList = [
            review for review in flaggedReviewList if getattr(review, "flagCount", 1) >= minFlags
        ]

    # Sorting
    if sortBy == "mostFlagged":
        flaggedReviewList = sorted(
            flaggedReviewList,
            key=lambda review: getattr(review, "flagCount", 1),
            reverse=True
        )

    # Pagination
    startIndex = (page - 1) * pageSize
    endIndex = startIndex + pageSize
    paginatedReviews = flaggedReviewList[startIndex:endIndex]

    return {
        "page": page,
        "pageSize": pageSize,
        "totalFlagged": len(flaggedReviewList),
        "pageCount": (len(flaggedReviewList) + pageSize - 1) // pageSize,
        "reviews": paginatedReviews
    }
