from typing import List, Dict, Any
from .repo import baseLoadAll, baseSaveAll, DATA_DIR

MOVIE_DATA_FILE = DATA_DIR / "movies.json"

def loadAll() -> List[Dict[str, Any]]:
    """
    Load all movies from the movies data file.

    Returns:
        List[Dict[str, Any]]: A list of movie items.
    """
    return baseLoadAll(MOVIE_DATA_FILE)

def saveAll(items: List[Dict[str, Any]]) -> None:
    """
    Save all movies to the movies data file.

    Args:
        items (List[Dict[str, Any]]): A list of movie items to save.
    """
    baseSaveAll(MOVIE_DATA_FILE, items)

__all__ = ["loadAll", "saveAll"]