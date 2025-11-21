from typing import List, Dict, Any
from .repo import _base_load_all, _base_save_all, DATA_DIR
from ..schemas.movie import Movie

MOVIE_DATA_FILE = DATA_DIR / "movies.json"

_MOVIE_CACHE: List[Movie] | None = None
_NEXT_MOVIE_ID: int | None = None


def getMaxMovieId(movies: List[Movie]) -> int:
    return max((m.id for m in movies), default=0)


def _load_movie_cache() -> List[Movie]:
    global _MOVIE_CACHE, _NEXT_MOVIE_ID

    if _MOVIE_CACHE is None:
        raw_dicts = _base_load_all(MOVIE_DATA_FILE)

        _MOVIE_CACHE = [Movie(**d) for d in raw_dicts]

        max_id = getMaxMovieId(_MOVIE_CACHE)
        _NEXT_MOVIE_ID = max_id + 1

    return _MOVIE_CACHE


def getNextMovieId() -> int:
    global _NEXT_MOVIE_ID
    if _NEXT_MOVIE_ID is None:
        _load_movie_cache()
    nid = _NEXT_MOVIE_ID
    _NEXT_MOVIE_ID += 1
    return nid


def loadMovies() -> List[Movie]:
    return _load_movie_cache()


def saveMovies(movies: List[Movie]) -> None:
    global _MOVIE_CACHE, _NEXT_MOVIE_ID

    _MOVIE_CACHE = movies

    max_id = getMaxMovieId(movies)
    if _NEXT_MOVIE_ID is None or _NEXT_MOVIE_ID <= max_id:
        _NEXT_MOVIE_ID = max_id + 1

    movie_dicts = [m.model_dump(mode="json") for m in movies]
    _base_save_all(MOVIE_DATA_FILE, movie_dicts)


def loadAll() -> List[Dict[str, Any]]:
    return [m.model_dump() for m in _load_movie_cache()]


def saveAll(movies: List[Movie | Dict[str, Any]]):
    movies = [m if isinstance(m, Movie) else Movie(**m) for m in movies]
    saveMovies(movies)
