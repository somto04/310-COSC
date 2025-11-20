from fastapi import APIRouter, HTTPException
from app.externalAPI.tmdbService import getMovieDetails, getRecommendations
from .tmdbSchema import TMDbMovie, TMDbRecommendation

router = APIRouter(prefix="/tmdb", tags=["tmdb"])


@router.get("/details/{movie_name}", response_model=TMDbMovie)
def movie_details(movie_name: str):
    """Fetch movie details from TMDB by movie name."""
    details = getMovieDetails(movie_name)
    if not details:
        raise HTTPException(status_code=404, detail="Movie not found")
    return details


@router.get("/recommendations/{movie_id}", response_model=list[TMDbRecommendation])
def movie_recommendations(movie_id: int):
    """Fetch movie recommendations from TMDB by movie ID."""
    return getRecommendations(movie_id)
