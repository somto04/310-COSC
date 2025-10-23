import uuid
from typing import List
from fastapi import HTTPException
from schemas.movie import Movie, MovieUpdate, MovieCreate
from repos.movieRepo import loadAll, saveAll #import functions to load and save movie data



def listMovies() -> List[Movie]:
    return [Movie(**it) for it in loadAll()] #load all movies from the repository and convert to Movie objects

def createMovie(payLoad: MovieCreate) -> Movie:
    movies = loadAll() #load existing movies from the repository
    newMovie = Movie()
    newId = str(uuid.uuid4()) #generate a unique ID for the new movie
    if any(it.get("id") == newId for it in movies):
        raise HTTPException(status_code=409, detail="ID collision; retry." )
    newMovie = Movie(
        id=newId,
        movieName = payLoad.movieName.strip(),
        yearReleased = payLoad.yearReleased,
        actors = payLoad.actors,
        genre = payLoad.genre.strip(),
        length = payLoad.length
    )
    movies.append(newMovie.model_dump()) #add the new movie to the list
    saveAll(movies) #save the updated movie list back to the repository
    return newMovie #returns the new movie object

def updateMovie(movieId: str, payLoad: MovieUpdate) -> Movie:
    movies = loadAll() #load existing movies from the repository
    for idx, it in enumerate(movies):
        if it.get("id") == movieId:
            updated = Movie(
                movieId = movieId,
                movieName = payLoad.movieName.strip(),
                yearReleased = payLoad.yearReleased,
                actors = payLoad.actors,
                genre = payLoad.genre.strip(),
                length = payLoad.length
            )
            movies[idx] = updated.model_dump() #update the movie in the list
            saveAll(movies) #save the updated movie list back to the repository
            return updated #return the updated movie object
    raise HTTPException(status_code=404, detail=f"Movie '{movieId}' not found")