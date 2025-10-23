from typing import List # imports the List function from the typing moduel for list creatio
from fastapi import APIRouter, HTTPException, status #creates a mini FastAPI for organizing related movie routes
from schemas.movie import Movie, MovieCreate, MovieUpdate #imports movie schemas for request and response validation
from services.movieService import listMovies, createMovie, updateMovie, deleteMovie, searchMovie 

#create a router object that will handle all routes starting with /movies
#tags organize the routes under the "movies" category in the API documentation
router = APIRouter(prefix = "/movies", tags = ["movies'])"])

#GET /movies - retrieves a list of all movies
@router.get("", responseModel = List[Movie]) #used camelcase for responseModel
def getMovies(): #retrieve a list of all movies from the database
    return listMovies() #return the list of movie objects from the database

#POST /movies - creates a new movie
@router.post("", responseModel = Movie, statusCode = 201)
def postMovie(payload: MovieCreate): #will create a new movie in the database
    return createMovie(payload) #return the newly created movie object

#PUT /movies - updates an existing movie 
@router.put("/{movieId}", responseModel = Movie)
def putMovie(movieId: str, payload: MovieUpdate): #update an existing movie in the database
    return updateMovie(movieId, payload) #return the updated movie object

#DELETE /movies - deletes a movie by its ID
@router.delete("/{movieId}", statusCode = 204)
def removeMovie(movieId: str): #delete a movie from the database
    deleteMovie(movieId) #perform the deletion operation
    return None #return no contentd

@router.get("/movies/search", response_model=List[Movie]) #added a search endpoint 
def searchMovies(query: str): #search for movies based on a query string
    #example: /movies/search?query=inception
    return searchMovie(query)

