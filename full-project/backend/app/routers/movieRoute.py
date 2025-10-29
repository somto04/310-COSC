
from typing import List, Optional
from app.routers.auth import requireAdmin
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
def getMovie(movieId: int):
    return getMovieById(movieId)

# ---------- #
# ADMIN ONLY #
# ---------- #
# admin: dict = Depends(requireAdmin) - require admin function has to return true

@router.post("", response_model=Movie, status_code=status.HTTP_201_CREATED)
def postMovie(payload: MovieCreate, admin: dict = Depends(requireAdmin)):
    return createMovie(payload)

@router.put("/{movieId}", response_model=Movie)
def putMovie(movieId: str, payload: MovieUpdate, admin: dict = Depends(requireAdmin)):
    return updateMovie(movieId, payload)

@router.delete("/{movieId}", status_code=status.HTTP_204_NO_CONTENT)
def removeMovie(movieId: str, admin: dict = Depends(requireAdmin)):
    deleteMovie(movieId)
    return None

