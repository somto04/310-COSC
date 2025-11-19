from fastapi import APIRouter, Depends, HTTPException, status
from auth import requireAdmin
from ..repos.reviewRepo import loadAll as loadReviews, saveAll as saveReviews
from ..utilities.penalties import incrementPenaltyForUser
from .reviewRoute import validateReview
from ..schemas.user import User

router = APIRouter(prefix="/admin", tags=["admin"])

@router.post("/reviews/{reviewId}/markInappropriate")
def markReviewInappropriate(reviewId: int, admin: User = Depends(requireAdmin)):
    reviews = loadReviews()
    review = next((r for r in reviews if int(r.get("id")) == int(reviewId)), None)
    validateReview(review)

    # Flag review
    review["flagged"] = True
    saveReviews(reviews)

    # Penalize author
    authorId = int(review.get("userId"))
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
    return [flagged for flagged in reviews if flagged.get("flagged") is True]
  

@router.get("/reports/reviews")
def getReportNotifications(currentUser: dict = Depends(getCurrentUser)):
    """
    Admin endpoint - return flagged review reports.
    Requires admin role.
    """
    if not currentUser or currentUser.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only")

    flagged = getFlaggedReviews()
    return {"count": len(flagged), "flagged": flagged}
