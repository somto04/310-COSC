import uuid
from typing import List
from fastapi import HTTPException
from ..schemas.review import Review, ReviewUpdate, ReviewCreate
from ..repos.reviewRepo import loadAll, saveAll
from ..repos import movieRepo


def searchReviews(query: str) -> List[Review]:
    """
    Search reviews by movie title (case-insensitive) or by movie ID.
    """
    q = (query or "").strip().lower()
    if not q:
        return []

    reviews = loadAll()
    movies = movieRepo.loadAll()
    matched_reviews = []

    # If query is a number → treat as movie ID
    if q.isdigit():
        for r in reviews:
            if str(r.get("movieId")) == q:
                matched_reviews.append(Review(**r))
        return matched_reviews

    # Otherwise, search for movie title
    matching_movie_ids = [
        str(m["id"]) for m in movies
        if q in str(m.get("title", "")).lower()
    ]

    for r in reviews:
        if str(r.get("movieId")) in matching_movie_ids:
            matched_reviews.append(Review(**r))

    return matched_reviews


def listReviews() -> List[Review]:
    return [Review(**it) for it in loadAll()]


def createReview(payload: ReviewCreate) -> Review:
    reviews = loadAll()
    # Generate a new unique ID for the review using uuid4
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

    # go through each review dict and if the ID matches, 
    # unpack it into a Review object and return it
    for review in reviews:
        if review.get("id") == reviewId:
            return Review(**review)
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
    # If we finish the loop without finding the review, raise 404
    raise HTTPException(status_code=404, detail=f"Review '{reviewId}' not found")


def deleteReview(reviewId: str) -> None:
    reviews = loadAll()

    # Filter out the review with the matching ID
    newReviews = [review for review in reviews if review.get("id") != reviewId]

    # If no review was removed, raise 404
    if len(newReviews) == len(reviews):
        raise HTTPException(status_code=404, detail=f"Review '{reviewId}' not found")
    
    saveAll(newReviews)
