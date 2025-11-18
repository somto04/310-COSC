# app/routers/adminReview.py
from fastapi import APIRouter, Depends, HTTPException, status
from auth import getCurrentUser
from ..repos.reviewRepo import loadAll as loadReviews, saveAll as saveReviews
from ..utilities.penalties import incrementPenaltyForUser

router = APIRouter(prefix="/admin", tags=["admin"])

@router.post("/reviews/{reviewId}/markInappropriate")
def markReviewInappropriate(reviewId: int, currentUser: dict = Depends(getCurrentUser)):
    if not currentUser or currentUser.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only")

    reviews = loadReviews()
    review = next((review for review in reviews if int(review.get("id")) == int(reviewId)), None)
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")

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
