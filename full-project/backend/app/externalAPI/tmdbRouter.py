from fastapi import APIRouter, HTTPException
from app.externalAPI.tmdbService import getMovieDetails, getRecommendations
from .tmdbSchema import TMDbMovie, TMDbRecommendation

router = APIRouter(prefix="/tmdb", tags=["tmdb"])


@router.get("/details/{movieName}", response_model=TMDbMovie)
def movieDetails(movieName: str):
    """Fetch movie details from TMDB by movie name."""
    details = getMovieDetails(movieName)
    if not details:
        raise HTTPException(status_code=404, detail="Movie not found")
    return details


@router.get("/recommendations/{movieId}", response_model=list[TMDbRecommendation])
def movieRecommendations(movieId: int):
    """Fetch movie recommendations from TMDB by movie ID."""
    return getRecommendations(movieId)
