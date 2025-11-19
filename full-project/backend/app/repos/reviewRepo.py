from typing import List, Dict, Any
from .repo import _base_load_all, _base_save_all, DATA_DIR
from ..schemas.review import Review

REVIEW_DATA_FILE = DATA_DIR / "reviews.json"

def loadAllReviews() -> List[Review]:
    """
    Load all reviews from the reviews data file.

    Returns:
        List[Review]: A list of review items.
    """
    items = _base_load_all(REVIEW_DATA_FILE)
    return [Review(**item) for item in items]
    
def saveAll(items: List[Review]) -> None:
    """
    Save all reviews to the reviews data file.

    Args:
        items (List[Review]): A list of review items to save.
    """
    items = [item.model_dump() for item in items]
    _base_save_all(REVIEW_DATA_FILE, items)

__all__ = ["loadAll", "saveAll"]