from typing import List
from .repo import _baseLoadAll, _baseSaveAll, DATA_DIR
from ..schemas.movie import Movie

MOVIE_DATA_FILE = DATA_DIR / "movies.json"

def loadAll() -> List[Movie]:
    """
    Load all movies as Pydantic Movie models.
    """
    raw = _baseLoadAll(MOVIE_DATA_FILE)
    return [Movie(**movie) for movie in raw]

def saveAll(items: List[Movie]) -> None:
    """
    Save all movies to the movies data file.
    """
    # Convert models back to dicts before saving
    raw = [movie.model_dump() for movie in items]
    _baseSaveAll(MOVIE_DATA_FILE, raw)

__all__ = ["loadAll", "saveAll"]
