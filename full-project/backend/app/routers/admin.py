from fastapi import APIRouter, Depends, HTTPException, status
from auth import requireAdmin
from ..repos.reviewRepo import loadAllReviews as loadReviews, saveAllReviews as saveReviews
from ..utilities.penalties import incrementPenaltyForUser
from .reviewRoute import validateReview

router = APIRouter(prefix="/admin", tags=["admin"])

@router.post("/reviews/{reviewId}/markInappropriate")
def markReviewInappropriate(reviewId: int, admin: dict = Depends(requireAdmin)):
    reviews = loadReviews()
    review = next((review for review in reviews if int(review.id) == int(reviewId)), None)
    validateReview(review)

    review.flagged = True
    saveReviews(reviews)

    authorId = int(review.userId)
    updatedUser = incrementPenaltyForUser(authorId)

    return {
        "message": "Review flagged and user penalized",
        "userId": updatedUser["id"],
        "penaltyCount": updatedUser.get("penaltyCount", 0),
        "isBanned": updatedUser.get("isBanned", False),
    }
