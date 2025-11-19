from fastapi import APIRouter, Depends, HTTPException, status
from auth import requireAdmin, getCurrentUser
from ..repos.reviewRepo import loadReviews, saveReviews
from ..utilities.penalties import incrementPenaltyForUser
from .reviewRoute import validateReview, getFlaggedReviews
from ..schemas.user import CurrentUser
from ..schemas.role import Role

router = APIRouter(prefix="/admin", tags=["admin"])

@router.post("/reviews/{reviewId}/markInappropriate")
def markReviewInappropriate(reviewId: int, admin: CurrentUser = Depends(requireAdmin)):
    reviews = loadReviews()
    review = next((review for review in reviews if review.Id == reviewId), None)
    validateReview(review)

    review.flagged = True
    saveReviews(reviews)

    authorId = int(review.userId)
    updatedUser = incrementPenaltyForUser(authorId)

    return {
        "message": "Review flagged and user penalized",
        "userId": updatedUser.id,
        "penaltyCount": updatedUser.penalties,
        "isBanned": updatedUser.isBanned,
    }

#only logged in users can flag a review
def getFlaggedReviews():
    """ Internal helper to get all flagged reviews
    
         reviews a list of all flagged reviews.  """
    reviews = loadReviews()
    return [review for review in reviews if review.flagged is True]
  

@router.get("/reports/reviews")
def getReportNotifications(currentUser: CurrentUser = Depends(getCurrentUser)):
    """
    Admin endpoint - return flagged review reports.
    Requires admin role.
    """

    # Typed Pydantic model, no dict access
    if currentUser.role != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin only"
        )

    flagged = getFlaggedReviews()

    return {
        "count": len(flagged),
        "flagged": flagged
    }