from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Depends
from app.routers.auth import requireAdmin
from ..schemas.user import CurrentUser
from app.schemas.movie import Movie, MovieCreate, MovieUpdate
from app.services.movieService import (
    listMovies,
    createMovie,
    getMovieById,
    updateMovie,
    deleteMovie,
    searchMovie,
    getMovieByFilter,
)

router = APIRouter(prefix="/movies", tags=["movies"])


@router.get("/search", response_model=List[Movie])
def searchMovies(query: Optional[str] = None):
    keyword = (query or "").lower().strip()

    results = searchMovie(keyword)

    if not results:
        raise HTTPException(status_code=404, detail="Movie not found")

    return results 


@router.get("/filter", response_model=List[Movie])
def filterMovies(
    genre: Optional[str] = None,
    year: Optional[int] = None,
    director: Optional[str] = None,
    star: Optional[str] = None,
):

    genreQuery = genre.lower().strip() if genre else None
    directorQuery = director.lower().strip() if director else None
    starQuery = star.lower().strip() if star else None

    results = getMovieByFilter(genreQuery, year, directorQuery, starQuery)

    if not results:
        raise HTTPException(status_code=404, detail="No movies found with the given filters")

    return results


@router.get("", response_model=List[Movie])
def getMovies():
    return listMovies()


@router.get("/{movieId}", response_model=Movie)
def getMovie(movieId: int):
    return getMovieById(movieId)



# ADMIN ONLY #

@router.post("", response_model=Movie, status_code=status.HTTP_201_CREATED)
def postMovie(payload: MovieCreate, admin: CurrentUser = Depends(requireAdmin)):
    return createMovie(payload)


@router.put("/{movieId}", response_model=Movie)
def putMovie(movieId: int, payload: MovieUpdate, admin: CurrentUser = Depends(requireAdmin)):
    return updateMovie(movieId, payload)


@router.delete("/{movieId}", status_code=status.HTTP_204_NO_CONTENT)
def removeMovie(movieId: int, admin: CurrentUser = Depends(requireAdmin)):
    deleteMovie(movieId)
    return None
