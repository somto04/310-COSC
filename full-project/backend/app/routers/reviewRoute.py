from typing import List
from fastapi import APIRouter, status, Depends, HTTPException
from ..schemas.review import Review, ReviewCreate, ReviewUpdate
from ..schemas.user import CurrentUser
from ..services.reviewService import (
    ReviewNotFoundError,
    flagReview,
    listReviews,
    createReview,
    deleteReview,
    updateReview,
    getReviewById,
    searchReviews,
)
from .authRoute import getCurrentUser, requireAdmin
from ..schemas.role import Role

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.get("/search", response_model=List[Review])
def searchReview(query: str = "", limit: int = 50, offset: int = 0):
    results = searchReviews(query)
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


@router.post("/{movieId}", response_model=Review, status_code=201)
def postReview(
    movieId: int,
    payload: ReviewCreate,
    currentUser: CurrentUser = Depends(getCurrentUser),
):
    """
    Create a new review for a movie. Requires authentication.

    Path params:
        movieId: ID of the movie the review is for

    Returns:
        The new review.
    """
    return createReview(movieId=movieId, userId=currentUser.id, payload=payload)


@router.get("/{reviewId}", response_model=Review)
def getReview(reviewId: int):
    return getReviewById(reviewId)


@router.put("/{reviewId}", response_model=Review)
def putReview(
    reviewId: int,
    payload: ReviewUpdate,
    currentUser: CurrentUser = Depends(getCurrentUser),
):
    """
    Update a review. Only the owner can update their review.

    Returns:
        The updated review.

    Raises:
        HTTPException: If the review doesn't exist or they are not the owner.
    """
    review = getReviewById(reviewId)
    validateReview(review)
    validateReviewOwner(currentUser, review)
    return updateReview(reviewId, payload)

@router.patch("/{reviewId}/flag", response_model=Review)
def markReviewAsInappropriate(
    reviewId: int,
    currentUser: CurrentUser = Depends(getCurrentUser),
):
    try:
        review = getReviewById(reviewId)
    except ReviewNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    
    try:
        updated = flagReview(reviewId)
    except ReviewNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    return updated


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
    if currentUser.role == Role.USER:
        validateReviewOwner(currentUser, review)
    else:
        requireAdmin(currentUser)
    deleteReview(reviewId)
    return None


def validateReview(review):
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")


def validateReviewOwner(currentUser, review):
    if review.userId != currentUser.id:
        raise HTTPException(status_code=403, detail="not authorised")
