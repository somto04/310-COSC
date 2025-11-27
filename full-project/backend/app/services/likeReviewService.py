from HTTP import HTTPException
from ..repos.likeReviewRepo import loadLikedReviews, saveLikedReviews
from ..repos.reviewRepo import loadReviews
from ..schemas.likedReviews import LikedReview


class ReviewNotFoundError(Exception):
    pass

class AlreadyLikedError(Exception):
    pass
 

def likeReview(userId: int, reviewId: int):
    """Like a review."""
    LikedReview = loadLikedReviews()
    reviews = loadReviews()
    if not any(review.id == reviewId for review in reviews):
        raise ReviewNotFoundError(f"Review '{reviewId}' not found")
    if any(liked.userId == userId and liked.reviewId == reviewId for liked in LikedReview):
        raise AlreadyLikedError(f"Review '{reviewId}' already liked by user '{userId}'")
    
    LikedReview.append(LikedReview(userId=userId, reviewId=reviewId))
    saveLikedReviews(LikedReview)
    return {"message": "Review liked"}

def unlikeReview(userId: int, reviewId: int):
    """Unlike a review."""
    LikedReview = loadLikedReviews()
    if not any(liked.userId == userId and liked.reviewId == reviewId for liked in LikedReview):
        raise ReviewNotFoundError(f"Liked ' {reviewId}' not found for user '{userId}'")
    # remove the liked review from the list of liked reviews
    newList = [
        liked for liked in LikedReview
        if not (liked.userId == userId and liked.reviewId == reviewId)
    ]
    saveLikedReviews(newList)
    return {"message": "Review unliked"}

def listLikedReviews(userId: int):
    """List all liked reviews for a user."""
    LikedReview = loadLikedReviews()
    reviews = loadReviews()
    likedReviewIds = [liked.reviewId for liked in LikedReview if liked.userId == userId]
    likedReviews = [review for review in reviews if review.id in likedReviewIds]
    return likedReviews


