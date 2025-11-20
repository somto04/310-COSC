from fastapi import APIRouter, Depends
from auth import requireAdmin
from ..repos.reviewRepo import loadReviews, saveReviews
from ..utilities.penalties import incrementPenaltyForUser
from .reviewRoute import validateReview
from ..schemas.user import CurrentUser

router = APIRouter(prefix="/admin", tags=["admin"])

#helper method to avoid redundancy
def reviewHasNext(reviewId: int) -> bool:
    reviews = loadReviews()
    review = next((review for review in reviews if review.Id == reviewId), None)
    return review is not None

#Adding accept/reject flag routes
@router.post("/reviews/{reviewId}/acceptFlag")
def acceptReviewFlag(reviewId: int, _: CurrentUser = Depends(requireAdmin)):
    """
    Admin accepts the flag.
    -> Penalize the review author
    -> Remove the review from flagged list (unflag it)
    """
    
    reviews = loadReviews()
    review = reviewHasNext(reviewId)
    validateReview(review)

    review.flagged = False
    
    authorId = review.userId
    updatedUser = incrementPenaltyForUser(authorId)
    saveReviews(reviews)

    return {"message": "Review flag accepted and cleared",
             "userId": updatedUser.id,
             "penaltyCount": updatedUser.penalties,
             "isBanned": updatedUser.isBanned}
    
@router.post("/reviews/{reviewId}/rejectFlag")
def rejectReviewFlag(reviewId: int, _: CurrentUser = Depends(requireAdmin)):
    """
    Admin rejects the flag.
    -> NO penalty
    -> Remove review from flagged list (unflag it)
    """
    reviews = loadReviews()
    review = reviewHasNext(reviewId)
    validateReview(review)
    # Just unflag, no penalty
    review.flagged = False
    saveReviews(reviews)

    return {
        "message": "Flag rejected. Review unflagged (no penalty applied).",
        "reviewId": reviewId
    }

@router.post("/reviews/{reviewId}/markInappropriate")
def markReviewInappropriate(reviewId: int, _: CurrentUser = Depends(requireAdmin)):
    reviews = loadReviews()
    review = reviewHasNext(reviewId)
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
  