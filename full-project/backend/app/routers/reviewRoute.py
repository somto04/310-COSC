from typing import List
from fastapi import APIRouter, status, Depends, HTTPException
from ..schemas.review import Review, ReviewCreate, ReviewUpdate
from ..services.reviewService import listReviews, createReview, deleteReview, updateReview, getReviewById, searchReviews
from .auth import getCurrentUser

router = APIRouter(prefix = "/reviews", tags = ["reviews"])

@router.get("/search", response_model=List[Review])
def searchReview(q: str = "", limit: int = 50, offset: int = 0):
    results = searchReviews(q)
    return results[offset : offset + limit]

@router.get("", response_model=List[Review])
def getReviews():
    return listReviews()

@router.post("", response_model=Review, status_code=201)
def postReview(payload: ReviewCreate, currentUser: dict = Depends(getCurrentUser)):
    """
    Create a new review. Requires authentication.

    Returns:
      The new review.
    """
    payload.userId = currentUser["id"]
    return createReview(payload)

@router.get("/{reviewId}", response_model = Review)
def getReview(reviewId: int):
    return getReviewById(reviewId)

@router.put("/{reviewId}", response_model = Review)
def putReview(reviewId: int, payload: ReviewUpdate, currentUser: dict = Depends(getCurrentUser)):
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
    payload.userId = currentUser["id"]
    return updateReview(reviewId, payload)

@router.delete("/{reviewId}", status_code=status.HTTP_204_NO_CONTENT)
def removeReview(reviewId: int, currentUser: dict = Depends(getCurrentUser)): 
    """
    Delete a review. Only admins or the owner can delete a review.

    Raises:
      HTTPException: If the review doesnt exist, they are not the owner or they're not an admin.
      """
    review = getReviewById(reviewId)
    validateReview(review)
    if currentUser["role"] != "admin":
        validateReviewOwner(currentUser, review)
    deleteReview(reviewId)
    return None

def validateReview(review):
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
def validateAdmin(currentUser):
    if currentUser["role"] != "admin":
        raise HTTPException(status_code=403, detail="not authorised")
    
def validateReviewOwner(currentUser, review):
    if review["username"] != currentUser["username"]:
        raise HTTPException(status_code=403, detail="not authorised")
    