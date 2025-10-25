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
    """Return all reviews as Review objects."""
    return [Review(**it) for it in loadAll()]


def createReview(payload: ReviewCreate) -> Review:
    """Create a new review and save it."""
    reviews = loadAll()
    newId = str(uuid.uuid4())

    if any(it.get("id") == newId for it in reviews):
        raise HTTPException(status_code=409, detail="ID collision; retry.")

    newReview = Review(
        id=newId,
        movieId=int(payload.movieId),
        userId=int(payload.userId),  # ✅ Added
        reviewTitle=payload.reviewTitle.strip(),
        rating=payload.rating.strip(),
        reviewBody=payload.reviewBody.strip(),
        datePosted=payload.datePosted or "Unknown",  # ✅ Safe fallback
        flagged=payload.flagged,
    )

    reviews.append(newReview.dict())
    saveAll(reviews)
    return newReview


def getReviewById(reviewId: str) -> Review:
    """Retrieve a single review by ID."""
    reviews = loadAll()
    for it in reviews:
        if it.get("id") == reviewId:
            return Review(**it)
    raise HTTPException(status_code=404, detail=f"Review '{reviewId}' not found")


def updateReview(reviewId: str, payload: ReviewUpdate) -> Review:
    """Update an existing review."""
    reviews = loadAll()
    for idx, it in enumerate(reviews):
        if it.get("id") == reviewId:
            updated = Review(
                id=reviewId,
                movieId=int(payload.movieId),
                userId=payload.userId or it.get("userId"),  # ✅ Added
                reviewTitle=payload.reviewTitle.strip(),
                rating=payload.rating.strip(),
                reviewBody=payload.reviewBody.strip(),
                datePosted=payload.datePosted or it.get("datePosted"),  # ✅ Preserve existing date
                flagged=payload.flagged,
            )
            reviews[idx] = updated.dict()
            saveAll(reviews)
            return updated
    raise HTTPException(status_code=404, detail=f"Review '{reviewId}' not found")


def deleteReview(reviewId: str) -> None:
    """Delete a review by ID."""
    reviews = loadAll()
    newReviews = [it for it in reviews if it.get("id") != reviewId]
    if len(newReviews) == len(reviews):
        raise HTTPException(status_code=404, detail=f"Review '{reviewId}' not found")
    saveAll(newReviews)
