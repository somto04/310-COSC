# ...existing code...
import uuid
from typing import List,Dict
from fastapi import HTTPException
from ..schemas.movie import Movie, MovieUpdate, MovieCreate
from ..repos.movieRepo import loadAll, saveAll  # import functions to load and save movie data

def listMovies() -> List[Movie]:
    data = loadAll()
    print("Loaded", len(data), "movies")
    # just return raw data for debugging
    return data

def createMovie(payload: MovieCreate) -> Movie:
    movies = loadAll()
    new_movie = payload.dict()
    new_movie["id"] = str(uuid.uuid4())
    movies.append(new_movie)
    saveAll(movies)
    return Movie(**new_movie)

# added/missing service functions required by routers
def getMovieById(movieId: str) -> Movie:
    for m in loadAll():
        if str(m.get("id")) == str(movieId):   # <-- convert both to string
            return Movie(**m)
    raise HTTPException(status_code=404, detail="Movie not found")

def updateMovie(movieId: str, payload: MovieUpdate) -> Movie:
    movies = loadAll()
    for idx, m in enumerate(movies):
        if m.get("id") == movieId:
            updates = payload.dict(exclude_unset=True)
            movies[idx] = {**m, **updates}
            saveAll(movies)
            return Movie(**movies[idx])
    raise HTTPException(status_code=404, detail="Movie not found")

def deleteMovie(movieId: str) -> None:
    movies = loadAll()
    filtered = [m for m in movies if m.get("id") != movieId]
    if len(filtered) == len(movies):
        raise HTTPException(status_code=404, detail="Movie not found")
    saveAll(filtered)

def _normalize_record(m: Dict) -> Dict:
    # produce minimal fields expected by your Movie schema
    out = {}
    out["id"] = str(m.get("id") or m.get("movieId") or "")
    out["title"] = m.get("title") or m.get("movieName") or ""
    # try to extract year from datePublished (YYYY-MM-DD) or fall back to yearReleased or 0
    dp = m.get("datePublished") or ""
    try:
        out["yearReleased"] = int(dp.split("-")[0]) if dp else int(m.get("yearReleased") or 0)
    except Exception:
        out["yearReleased"] = int(m.get("yearReleased") or 0)
    out["actors"] = m.get("mainStars") or m.get("actors") or []
    out["genre"] = (m.get("movieGenres")[0] if isinstance(m.get("movieGenres"), list) and m.get("movieGenres") else m.get("genre") or "") 
    out["duration"] = int(m.get("duration") or m.get("length") or 0)
    return out

def searchMovie(query: str) -> List[Movie]:
    q = (query or "").lower().strip()
    if not q:
        return []

    results = []
    for m in loadAll():
        # check across multiple fields
        title = str(m.get("title", "")).lower()
        desc = str(m.get("description", "")).lower()
        genres = " ".join(m.get("movieGenres", []))
        stars = " ".join(m.get("mainStars", []))
        directors = " ".join(m.get("directors", []))

        if any(q in field for field in [title, desc, genres, stars, directors]):
            normalized = {
                "id": m.get("id"),
                "title": m.get("title"),
                "movieIMDbRating": m.get("movieIMDbRating"),
                "movieGenres": m.get("movieGenres"),
                "directors": m.get("directors"),
                "mainStars": m.get("mainStars"),
                "description": m.get("description"),
                "datePublished": m.get("datePublished"),
                "duration": m.get("duration"),
            }
            results.append(normalized)
    return results
