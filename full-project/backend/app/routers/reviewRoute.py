from typing import List
from fastapi import APIRouter, status
from schemas.review import Review, ReviewCreate, ReviewUpdate
from services.reviewService import listReviews, createReview, deleteReview, updateReview, getReviewById

router = APIRouter(prefix = "/reviews", tags = ["reviews"])

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
def removeReview(reviewId: str):
    deleteReview(reviewId)
    return None