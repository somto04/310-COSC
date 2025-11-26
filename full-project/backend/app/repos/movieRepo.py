from typing import List
from .repo import _baseLoadAll, _baseSaveAll, DATA_DIR
from app.schemas.movie import Movie

MOVIE_DATA_PATH = DATA_DIR / "movies.json"
_MOVIE_CACHE: List[Movie] | None = None
_NEXT_MOVIE_ID: int | None = None

def _getMaxMovieId(movies: List[Movie]) -> int:
    """
    Return the maximum Movie ID in a list of movies, or 0 if empty.
    """
    return max((movie.id for movie in movies), default=0)


def _loadMovieCache() -> List[Movie]:
    """
    Load movies from the data file into a cache.

    Loads the movies only once and caches them for future calls.
    Returns:
        List[Movie]: A list of movies.
    """
    global _MOVIE_CACHE, _NEXT_MOVIE_ID
    if _MOVIE_CACHE is None:
        movie_dicts = _baseLoadAll(MOVIE_DATA_PATH)
        _MOVIE_CACHE = [Movie(**movie) for movie in movie_dicts]

        maxId = _getMaxMovieId(_MOVIE_CACHE)
        _NEXT_MOVIE_ID = maxId + 1
    return _MOVIE_CACHE

def getNextMovieId() -> int:
    """
    Get the next available movie ID.

    Returns:
        int: The next movie ID.
    """
    global _NEXT_MOVIE_ID
    if _NEXT_MOVIE_ID is None:
        _loadMovieCache()

    assert _NEXT_MOVIE_ID is not None

    next_id = _NEXT_MOVIE_ID
    _NEXT_MOVIE_ID += 1
    return next_id


def loadMovies() -> List[Movie]:
    """
    Load all movies from the movies data file.
    Returns:
        List[Movie]: A list of movie items.
    """
    return _loadMovieCache()


def saveMovies(movies: List[Movie]) -> None:
    """
    Save all movies to the movies data file.
    Args:
        movies (List[Movie]): A list of movie items to save.
    """
    global _MOVIE_CACHE, _NEXT_MOVIE_ID
    _MOVIE_CACHE = movies

    maxId = _getMaxMovieId(movies)
    if _NEXT_MOVIE_ID is None or _NEXT_MOVIE_ID <= maxId:
        _NEXT_MOVIE_ID = maxId + 1

    movie_dicts = [movie.model_dump() for movie in movies]
    _baseSaveAll(MOVIE_DATA_PATH, movie_dicts)


__all__ = ["loadMovies", "saveMovies"]
