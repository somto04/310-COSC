from typing import List, Dict, Any
from .repo import _base_load_all, _base_save_all, DATA_DIR
from ..schemas.review import Review

REVIEW_DATA_PATH = DATA_DIR / "reviews.json"
_REVIEW_CACHE: List[Review] | None = None

def _load_review_cache() -> List[Review]:
    """
    Load reviews from the data file into a cache.

    Loads the reviews only once and caches them for future calls.
    Returns:
        List[Review]: A list of reviews.
    """
    global _REVIEW_CACHE
    if _REVIEW_CACHE is None:
        review_dicts = _base_load_all(_REVIEW_CACHE)
        _REVIEW_CACHE = [Review(**review) for review in review_dicts]
    return _REVIEW_CACHE

def loadReviews() -> List[Review]:
    """
    Load all reviews from the reviews data file.

    Returns:
        List[Review]: A list of review items.
    """
    return _load_review_cache
    
def saveReviews(reviews: List[Review]) -> None:
    """
    Save all reviews to the reviews data file.

    Args:
        reviews (List[Review]): A list of review items to save.
    """
    global _REVIEW_CACHE
    _REVIEW_CACHE = reviews
    review_dict = [review.model_dump() for review in reviews]
    _base_save_all(REVIEW_DATA_PATH, review_dict)

__all__ = ["loadAll", "saveAll"]