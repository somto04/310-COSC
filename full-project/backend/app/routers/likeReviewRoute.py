from fastapi import APIRouter, Depends, HTTPException
from ..services.likeReviewService import likeReview, unlikeReview, listLikedReviews, ReviewNotFoundError, AlreadyLikedError
from ..schemas.user import CurrentUser
from ..routers.authRoute import getCurrentUser

router = APIRouter(prefix = "/likeReview", tags = ["likedReviews"])

@router.post("/{reviewId}", status_code=201)
def likeAReview(reviewId: int, currentUser: CurrentUser = Depends(getCurrentUser)):
    """Like a review."""
    try:
        return likeReview(currentUser.id, reviewId)
    except ReviewNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except AlreadyLikedError as e:
        raise HTTPException(status_code=409, detail=str(e))

@router.delete("/{reviewId}")
def unlikeAReview(reviewId: int, currentUser: CurrentUser = Depends(getCurrentUser)):
    """Unlike a review."""
    try:
        return unlikeReview(currentUser.id, reviewId)
    except ReviewNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/")
def getLikedReviews(currentUser: CurrentUser = Depends(getCurrentUser)):
    """Get all liked reviews for the current user."""
    try:
        return listLikedReviews(currentUser.id)
    except ReviewNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
