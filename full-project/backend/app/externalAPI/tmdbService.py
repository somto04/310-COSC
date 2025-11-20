import requests
import os
from dotenv import load_dotenv
from app.schemas.tmdb import TMDbMovie, TMDbRecommendation

load_dotenv()

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
BASE_URL = "https://api.themoviedb.org/3"


def getMovieDetails(movieName: str) -> TMDbMovie | None:
    """Retrieve main movie details from TMDb"""
    
    response = requests.get(
        f"{BASE_URL}/search/movie",
        params={"api_key": TMDB_API_KEY, "query": movieName}
    )


def getMovieDetails(movieName: str) -> TMDbMovie | None:
    """Retrieve main movie details from TMDb"""
    
    response = requests.get(
        f"{BASE_URL}/search/movie",
        params={"api_key": TMDB_API_KEY, "query": movieName}
    )

    data = response.json()

    if not data.get("results"):
        return None

    movie = data["results"][0]

    return TMDbMovie(
        id=movie["id"],
        title=movie["title"],
        poster=f"https://image.tmdb.org/t/p/w500{movie['poster_path']}"
                if movie.get("poster_path") else None,
        overview=movie.get("overview"),
        rating=movie.get("vote_average"),
    )


def getRecommendations(movieId: int) -> list[TMDbRecommendation]:
    """Fetch movie recommendations from TMDb"""

    response = requests.get(
        f"{BASE_URL}/movie/{movieId}/recommendations",
        params={"api_key": TMDB_API_KEY}
    )

    data = response.json()

    results = data.get("results", [])

    return [
        TMDbRecommendation(
            id=m["id"],
            title=m["title"],
            poster=f"https://image.tmdb.org/t/p/w500{m['poster_path']}"
                    if m.get("poster_path") else None,
            rating=m.get("vote_average"),
        )
        for m in results[:5]
    ]
