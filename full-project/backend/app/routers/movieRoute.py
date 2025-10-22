
from typing import List
from fastapi import APIRouter, HTTPException, status
from ..schemas.movie import Movie, MovieCreate, MovieUpdate
from ..services.movieService import (
    listMovies,
    createMovie,
    getMovieById,
    updateMovie,
    deleteMovie,
    searchMovie,
)

router = APIRouter(prefix="/movies", tags=["movies"])

@router.get("", response_model=List[Movie])
def getMovies():
    return listMovies()

@router.post("", response_model=Movie, status_code=status.HTTP_201_CREATED)
def postMovie(payload: MovieCreate):
    return createMovie(payload)

@router.get("/{movieId}", response_model=Movie)
def getMovie(movieId: str):
    return getMovieById(movieId)

@router.put("/{movieId}", response_model=Movie)
def putMovie(movieId: str, payload: MovieUpdate):
    return updateMovie(movieId, payload)

@router.delete("/{movieId}", status_code=status.HTTP_204_NO_CONTENT)
def removeMovie(movieId: str):
    deleteMovie(movieId)
    return None

@router.get("/search", response_model=List[Movie])
def searchMovies(query: str):
    return searchMovie(query)
