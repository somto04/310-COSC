import uuid
from typing import List
from fastAPI import HTTPException
from schemas.movie import Movie, MovieUpdate, MovieCreate
from repos.movieRepo import loadAll, saveAll #import functions to load and save movie data

def listMovies() -> List[Movie]:
    return [Movie(**it) for it in loadAll()] #load all movies from the repository and convert to Movie objects
def createMovie(payload: MovieCreate) -> Movie