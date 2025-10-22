# ...existing code...
import uuid
from typing import List
from fastapi import HTTPException
from ..schemas.movie import Movie, MovieUpdate, MovieCreate
from ..repos.movieRepo import loadAll, saveAll  # import functions to load and save movie data

def listMovies() -> List[Movie]:
    return [Movie(**it) for it in loadAll()]  # load all movies and convert to Movie objects

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
        if m.get("id") == movieId:
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

def searchMovie(query: str) -> List[Movie]:
    q = query.lower()
    results = []
    for m in loadAll():
        text = " ".join([str(m.get(k, "")).lower() for k in ("title", "overview")])
        if q in text:
            results.append(Movie(**m))
    return results
# ...existing code...