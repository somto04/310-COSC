from ..repos.likeReviewRepo import loadLikedReviews, saveLikedReviews
from ..repos.reviewRepo import loadReviews
from ..schemas.likedReviews import LikedReview, LikedReviewFull
from ..services.userService import getUserById
from ..services.movieService import getMovieById
from ..externalAPI.tmdbService import getMovieDetailsById


class ReviewNotFoundError(Exception):
    pass

class AlreadyLikedError(Exception):
    pass


def likeReview(userId: int, reviewId: int):
    """Like a review."""
    likedReviews = loadLikedReviews()  # FIX: renamed variable
    reviews = loadReviews()

    # Check if the review exists
    if not any(review.id == reviewId for review in reviews):
        raise ReviewNotFoundError(f"Review '{reviewId}' not found")

    # Check if user already liked this review
    if any(liked.userId == userId and liked.reviewId == reviewId for liked in likedReviews):
        raise AlreadyLikedError(f"Review '{reviewId}' already liked by user '{userId}'")

    # Add new liked review
    likedReviews.append(
        LikedReview(userId=userId, reviewId=reviewId)
    )

    saveLikedReviews(likedReviews)
    return {"message": "Review liked"}


def unlikeReview(userId: int, reviewId: int):
    """Unlike a review."""
    likedReviews = loadLikedReviews()  # FIX: renamed variable

    if not any(liked.userId == userId and liked.reviewId == reviewId for liked in likedReviews):
        raise ReviewNotFoundError(f"Liked review '{reviewId}' not found for user '{userId}'")

    # Remove the entry
    newList = [
        liked for liked in likedReviews
        if not (liked.userId == userId and liked.reviewId == reviewId)
    ]

    saveLikedReviews(newList)
    return {"message": "Review unliked"}


def listLikedReviews(userId: int):
    """List all liked reviews for a user."""
    likedReviews = loadLikedReviews()  #renamed variable
    reviews = loadReviews()

    likedReviewIds = [liked.reviewId for liked in likedReviews if liked.userId == userId]

    result = []

    for review in reviews:
        if review.id in likedReviewIds:

            
            user = getUserById(review.userId)

            movie = getMovieById(review.movieId)

            tmdbDetails = getMovieDetailsById(movie.tmdbId)
            poster_url = tmdbDetails.poster if hasattr(tmdbDetails, "poster") else None

            result.append(
                LikedReviewFull(
                    id=review.id,
                    movieId=review.movieId,
                    movieTitle=movie.title,
                    username=user.username,
                    reviewTitle=review.reviewTitle,
                    poster=poster_url,
                )
            )

    return result
