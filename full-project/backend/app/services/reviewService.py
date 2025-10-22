import uuid
from typing import List
from fastapi import HTTPException
from ..schemas.review import Review, ReviewUpdate, ReviewCreate
from ..repos.reviewRepo import loadAll, saveAll

def listReviews() -> List[Review]:
    return [Review(**it) for it in loadAll()]

def createReview(payload: ReviewCreate) -> Review:
    reviews = loadAll()
    newId = str(uuid.uuid4())
    if any(it.get("id") == newId for it in reviews):
        raise HTTPException(status_code=409, detail="ID collision; retry.")
    newReview = Review(id=newId, 
                   movieId = payload.movieId.strip(), 
                   reviewTitle = payload.reviewTitle.strip(), 
                   rating = payload.rating.strip(),
                   reviewBody = payload.reviewBody.strip(),
                   flagged = payload.flagged)
    reviews.append(newReview.dict())
    saveAll(reviews)
    return newReview

def getReviewById(reviewId: str) -> Review:
    reviews = loadAll()
    for it in reviews:
        if it.get("id") == reviewId:
            return Review(**it)
    raise HTTPException(status_code=404, detail=f"Review '{reviewId}' not found")

def updateReview(reviewId: str, payload: ReviewUpdate) -> Review:
    reviews = loadAll()
    for idx, it in enumerate(reviews):
        if it.get("id") == reviewId:
            updated = Review(
                id=reviewId,
                movieId = payload.movieId.strip(), 
                reviewTitle = payload.reviewTitle.strip(), 
                rating = payload.rating.strip(),
                reviewBody = payload.reviewBody.strip(),
                flagged = payload.flagged,
            )
            reviews[idx] = updated.dict()
            saveAll(reviews)
            return updated
    raise HTTPException(status_code=404, detail=f"Review '{reviewId}' not found")

def deleteReview(reviewId: str) -> None:
    reviews = loadAll()
    newReviews = [it for it in reviews if it.get("id") != reviewId]
    if len(newReviews) == len(reviews):
        raise HTTPException(status_code=404, detail=f"Review '{reviewId}' not found")
    saveAll(newReviews)