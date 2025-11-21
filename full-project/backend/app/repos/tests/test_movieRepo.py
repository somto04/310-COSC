from typing import List
from ..repo import _base_load_all, _base_save_all, DATA_DIR
from ...schemas.movie import Movie

MOVIE_DATA_PATH = DATA_DIR / "movies.json"

# Cache + ID counter
_MOVIE_CACHE: List[Movie] | None = None
_NEXT_MOVIE_ID: int | None = None


def getMaxMovieId(movies: List[Movie]) -> int:
    """
    Return the maximum Movie ID in a list of movies, or 0 if empty.
    """
    return max((movie.id for movie in movies), default=0)


def _load_movie_cache() -> List[Movie]:
    """
    Load movies from disk ONCE and cache them.
    Converts raw dicts -> Movie models.
    """
    global _MOVIE_CACHE, _NEXT_MOVIE_ID

    if _MOVIE_CACHE is None:
        movie_dicts = _base_load_all(MOVIE_DATA_PATH)  # returns dicts

        # Convert dicts -> Movie models
        _MOVIE_CACHE = [Movie(**movie) for movie in movie_dicts]

        # Initialise next ID
        maxId = getMaxMovieId(_MOVIE_CACHE)
        _NEXT_MOVIE_ID = maxId + 1

    return _MOVIE_CACHE


def getNextMovieId() -> int:
    """
    Get the next available movie ID.
    Auto-initializes if needed.
    """
    global _NEXT_MOVIE_ID

    if _NEXT_MOVIE_ID is None:
        _load_movie_cache()

    assert _NEXT_MOVIE_ID is not None

    next_id = _NEXT_MOVIE_ID
    _NEXT_MOVIE_ID += 1
    return next_id


def loadMovies() -> List[Movie]:
    """
    Return cached movies (as Movie models).
    """
    return _load_movie_cache()


def saveMovies(movies: List[Movie]) -> None:
    """
    Save Movie models to disk as dicts.
    """
    global _MOVIE_CACHE, _NEXT_MOVIE_ID

    # Update cache
    _MOVIE_CACHE = movies

    # Recalculate ID counter
    maxId = getMaxMovieId(movies)
    if _NEXT_MOVIE_ID is None or _NEXT_MOVIE_ID <= maxId:
        _NEXT_MOVIE_ID = maxId + 1

    # Convert models -> dicts for JSON saving
    movie_dicts = [movie.model_dump() for movie in movies]

    _base_save_all(MOVIE_DATA_PATH, movie_dicts)


__all__ = ["loadMovies", "saveMovies", "getNextMovieId"]
