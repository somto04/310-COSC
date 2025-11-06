from typing import List, Dict, Any
from .repo import _base_load_all, _base_save_all, DATA_DIR

REVIEW_DATA_FILE = DATA_DIR / "reviews.json"

def loadAll() -> List[Dict[str, Any]]:
    """
    Load all reviews from the reviews data file.

    Returns:
        List[Dict[str, Any]]: A list of review items.
    """
    return _base_load_all(REVIEW_DATA_FILE)
    
def saveAll(items: List[Dict[str, Any]]) -> None:
    """
    Save all reviews to the reviews data file.

    Args:
        items (List[Dict[str, Any]]): A list of review items to save.
    """
    _base_save_all(REVIEW_DATA_FILE, items)

__all__ = ["loadAll", "saveAll"]