from typing import List, Dict, Any
from .repo import baseLoadAll, baseSaveAll, DATA_DIR
from ..schemas.review import Review

REVIEW_DATA_PATH = DATA_DIR / "reviews.json"
_REVIEW_CACHE: List[Review] | None = None
_NEXT_REVIEW_ID: int | None = None

def getMaxReviewId(reviews: List[Review]) -> int:
    """
    Return the maximum Review ID in a list of reviews, or 0 if empty.
    """
    return max((review.id for review in reviews), default=0)


def loadReviewCache() -> List[Review]:
    """
    Load reviews from the data file into a cache.

    Loads the reviews only once and caches them for future calls.
    Returns:
        List[Review]: A list of reviews.
    """
    global _REVIEW_CACHE, _NEXT_REVIEW_ID
    if _REVIEW_CACHE is None:
        review_dicts = baseLoadAll(REVIEW_DATA_PATH)
        _REVIEW_CACHE = [Review(**review) for review in review_dicts]

        maxId = getMaxReviewId(_REVIEW_CACHE)
        _NEXT_REVIEW_ID = maxId + 1
    return _REVIEW_CACHE

def getNextReviewId() -> int:
    """
    Get the next available review ID.

    Returns:
        int: The next review ID.
    """
    global _NEXT_REVIEW_ID
    if _NEXT_REVIEW_ID is None:
        loadReviewCache()

    assert _NEXT_REVIEW_ID is not None

    next_id = _NEXT_REVIEW_ID
    _NEXT_REVIEW_ID += 1
    return next_id


def loadReviews() -> List[Review]:
    """
    Load all reviews from the reviews data file.

    Returns:
        List[Review]: A list of review items.
    """
    return loadReviewCache()
    
def saveReviews(reviews: List[Review]) -> None:
    """
    Save all reviews to the reviews data file.

    Args:
        reviews (List[Review]): A list of review items to save.
    """
    global _REVIEW_CACHE, _NEXT_REVIEW_ID
    _REVIEW_CACHE = reviews

    maxId = getMaxReviewId(reviews)
    if _NEXT_REVIEW_ID is None or _NEXT_REVIEW_ID <= maxId:
        _NEXT_REVIEW_ID = maxId + 1

    review_dict = [review.model_dump() for review in reviews]
    baseSaveAll(REVIEW_DATA_PATH, review_dict)

__all__ = ["loadReviews", "saveReviews"]