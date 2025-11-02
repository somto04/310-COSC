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
def postReview(payload: ReviewCreate):
    return createReview(payload)

@router.get("/{reviewId}", response_model = Review)
def getReview(reviewId: str):
    return getReviewById(reviewId)

@router.put("/{reviewId}", response_model = Review)
def putReview(reviewId: str, payload: ReviewUpdate):
    return updateReview(reviewId, payload)

@router.delete("/{reviewId}", status_code=status.HTTP_204_NO_CONTENT)
# gets the current user from auth
def removeReview(reviewId: str, currentUser: dict = Depends(getCurrentUser)): 
    review = getReviewById(reviewId)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    if currentUser["role"] != "admin" and review["username"] != currentUser["username"]:
        raise HTTPException(status_code=403, detail="not authorised to delete this review")
    deleteReview(reviewId)
    return None