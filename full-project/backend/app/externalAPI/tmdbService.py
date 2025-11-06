import requests
import os
from dotenv import load_dotenv

load_dotenv()

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
BASE_URL = "https://api.themoviedb.org/3"

def getMovieDetails(movie_name: str):
    """Retrieve movie details (poster, rating, overview) from TMDb"""
    url = f"{BASE_URL}/search/movie"
    params = {"api_key": TMDB_API_KEY, "query": movie_name}
    response = requests.get(url, params=params)
    data = response.json()

    if not data["results"]:
        return None

    movie = data["results"][0]  # first result match
    return {
        "title": movie["title"],
        "poster": f"https://image.tmdb.org/t/p/w500{movie['poster_path']}" if movie.get("poster_path") else None,
        "overview": movie.get("overview"),
        "rating": movie.get("vote_average"),
        "id": movie.get("id"),
    }

def getRecommendations(movie_id: int):
    """Fetch movie recommendations from TMDb"""
    url = f"{BASE_URL}/movie/{movie_id}/recommendations"
    params = {"api_key": TMDB_API_KEY}
    response = requests.get(url, params=params)
    data = response.json()

    if "results" not in data:
        return []

    return [
        {
            "title": m["title"],
            "poster": f"https://image.tmdb.org/t/p/w500{m['poster_path']}" if m.get("poster_path") else None,
            "rating": m.get("vote_average"),
        }
        for m in data["results"][:5]  # limit to 5
    ]
