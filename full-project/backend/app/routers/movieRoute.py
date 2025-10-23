
import json
from typing import List, Optional
from app.auth import getCurrentUser
from fastapi import APIRouter, HTTPException, status, Depends
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

@router.get("/search", response_model=List[Movie])
def searchMovies(q: Optional[str] = None, query: Optional[str] = None):
    keyword = q or query or ""
    results = searchMovie(keyword)
    if not results:
        raise HTTPException(status_code=404, detail="Movie not found")
    return results

@router.get("", response_model=List[Movie])
def getMovies():
    return listMovies()

@router.get("/{movieId}", response_model=Movie)
def getMovie(movieId: str):
    return getMovieById(movieId)

# -------------- #
#   ADMIN ONLY   #
# -------------- #

@router.post("", response_model=Movie, status_code=status.HTTP_201_CREATED)
def postMovie(payload: MovieCreate, currentUser: dict = Depends(getCurrentUser)):
    if currentUser["role"] != "admin":
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail = "only admins can add movies"
        )
    return createMovie(payload)

@router.put("/{movieId}", response_model=Movie)
def putMovie(
    movieId: str, 
    payload: MovieUpdate,
    currentUser: dict = Depends(getCurrentUser)): # gets the current user in order to check their role
    if currentUser["role"] != "admin": # if the current user is not an admin then throw exception
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail = "only admins can add movies"
        )
    return updateMovie(movieId, payload)

@router.delete("/{movieId}", status_code=status.HTTP_204_NO_CONTENT)
def removeMovie(
    movieId: str,
    currentUser: dict = Depends(getCurrentUser)):
    if currentUser["role"] != "admin": 
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail = "only admins can add movies"
        )
    deleteMovie(movieId)
    return None

