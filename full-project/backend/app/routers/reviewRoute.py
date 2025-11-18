from typing import List
from fastapi import APIRouter, status, Depends, HTTPException
from ..schemas.review import Review, ReviewCreate, ReviewUpdate
from ..schemas.user import CurrentUser
from ..services.reviewService import listReviews, createReview, deleteReview, updateReview, getReviewById, searchReviews
from .auth import getCurrentUser, requireAdmin

router = APIRouter(prefix="/reviews", tags=["reviews"])

@router.get("/search", response_model=List[Review])
def searchReview(q: str = "", limit: int = 50, offset: int = 0):
    results = searchReviews(q)
    return results[offset : offset + limit]

@router.get("", response_model=List[Review])
def getReviews(page: int = 1, limit: int = 10):
    """
    Returns paginated reviews.
    
    """
    # Make sure page and limit are valid
    if page < 1:
        page = 1
    if limit < 1:
        limit = 10

    reviews = listReviews()  # returns full list

    # Calculate pagination slice
    start = (page - 1) * limit
    end = start + limit

    return reviews[start:end]


@router.get("/flagged", response_model=List[Review])
def getFlaggedReviews():
    reviews = listReviews()
    return [review for review in reviews if review.flagged is True]

@router.post("", response_model=Review, status_code=201)
def postReview(payload: ReviewCreate, currentUser: CurrentUser = Depends(getCurrentUser)):
    """
    Create a new review. Requires authentication.

    Returns:
      The new review.
    """
    payload.userId = currentUser.id
    return createReview(payload)

@router.get("/{reviewId}", response_model=Review)
def getReview(reviewId: int):
    return getReviewById(reviewId)

@router.put("/{reviewId}", response_model = Review)
def putReview(reviewId: int, payload: ReviewUpdate, currentUser: CurrentUser = Depends(getCurrentUser)):
    """
    Update a review. Only the owner can update their review.

    Returns:
      The updated review.

    Raises:
      HTTPException: If the review doesnt exist or they are not the owner.
      """
    review = getReviewById(reviewId)
    validateReview(review)
    validateReviewOwner(currentUser, review)
    payload.userId = currentUser.id
    return updateReview(reviewId, payload)

@router.delete("/{reviewId}", status_code=status.HTTP_204_NO_CONTENT)
def removeReview(reviewId: int, currentUser: CurrentUser = Depends(getCurrentUser)):
    """
    Makes sure that only review owners and admins can delete reviews.

    Returns:
        204 No Content on successful deletion
    
    Raises:
        HTTPException: If the review isn't found or they are not the owner or an admin.
    """
    review = getReviewById(reviewId)
    validateReview(review)
    if currentUser.role != "admin":
        validateReviewOwner(currentUser, review)
    else:
        requireAdmin(currentUser)
    deleteReview(reviewId)
    return None

def validateReview(review):
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
def validateReviewOwner(currentUser, review):
    if review["username"] != currentUser["username"]:
        raise HTTPException(status_code=403, detail="not authorised")
    
