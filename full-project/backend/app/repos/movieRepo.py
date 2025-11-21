from typing import List, Dict, Any
from .repo import _baseLoadAll, _baseSaveAll, DATA_DIR
from ..schemas.movie import Movie

MOVIE_DATA_FILE = DATA_DIR / "movies.json"
_MOVIE_CACHE: List[Movie] | None = None
_NEXT_MOVIE_ID: int | None = None


def getMaxMovieId(movies: List[Movie]) -> int:
    return max((m.id for m in movies), default=0)


def loadMovieCache() -> List[Movie]:
    global _MOVIE_CACHE, _NEXT_MOVIE_ID

    if _MOVIE_CACHE is None:
        raw_dicts = _baseLoadAll(MOVIE_DATA_FILE)

        _MOVIE_CACHE = [Movie(**d) for d in raw_dicts]

        max_id = getMaxMovieId(_MOVIE_CACHE)
        _NEXT_MOVIE_ID = max_id + 1

    return _MOVIE_CACHE


def getNextMovieId() -> int:
    global _NEXT_MOVIE_ID
    if _NEXT_MOVIE_ID is None:
        loadMovieCache()
    nid = _NEXT_MOVIE_ID
    _NEXT_MOVIE_ID += 1
    return nid


def loadMovies() -> List[Movie]:
    """
    Load all movies from the movies data file.

    Returns:
        List[Movie]: A list of movie items.
    """
    return loadMovieCache()


def saveMovies(movies: List[Movie]) -> None:
    """
    Save all movies to the movies data file.

    Args:
        movies (List[Movie]): A list of movie items to save.
    """
    global _MOVIE_CACHE, _NEXT_MOVIE_ID

    _MOVIE_CACHE = movies

    maxId = getMaxMovieId(movies)
    if _NEXT_MOVIE_ID is None or _NEXT_MOVIE_ID <= maxId:
        _NEXT_MOVIE_ID = maxId + 1

    movie_dicts = [m.model_dump(mode="json") for m in movies]
    _baseSaveAll(MOVIE_DATA_FILE, movie_dicts)


def loadAll() -> List[Dict[str, Any]]:
    return [m.model_dump() for m in loadMovieCache()] 


def saveAll(movies: List[Movie | Dict[str, Any]]):
    movies = [m if isinstance(m, Movie) else Movie(**m) for m in movies]
    saveMovies(movies)  
