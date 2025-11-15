from fastapi import APIRouter, Depends, HTTPException, status
from auth import requireAdmin
from ..repos.reviewRepo import loadAll as loadReviews, saveAll as saveReviews
from ..utilities.penalties import incrementPenaltyForUser
from .reviewRoute import validateReview

router = APIRouter(prefix="/admin", tags=["admin"])

@router.post("/reviews/{reviewId}/markInappropriate")
def markReviewInappropriate(reviewId: int, admin: dict = Depends(requireAdmin)):
    reviews = loadReviews()
    review = next((r for r in reviews if int(r.get("id")) == int(reviewId)), None)
    validateReview(review)

    review["flagged"] = True
    saveReviews(reviews)

    authorId = int(review.get("userId"))
    updatedUser = incrementPenaltyForUser(authorId)

    return {
        "message": "Review flagged and user penalized",
        "userId": updatedUser["id"],
        "penaltyCount": updatedUser.get("penaltyCount", 0),
        "isBanned": updatedUser.get("isBanned", False),
    }
