import pytest
from fastapi.testclient import TestClient

#one integration test: testing MovieRouter
def test_GetMovies():
    from app.model.main import app #import the main FastAPI app instance
    client = TestClient(app) #create a test client for the FastAPI app
    response = client.get("/movies") #send a GET request to the /movies endpoint
    assert response.status_code == 200 #assert that the response status code is 200 meaning success
    assert isinstance(response.json(), list) #assert that the reponse body is a list
    
def test_CreateMovie():
    from app.model.main import app
    client = TestClient(app)
    #create a movie
    newMovie = {
        "title": "Test Movie",
        "director": "Test Director",
        "year": 2024,
        "genre": "Test Genre",
        "id": 1234
    }
    createResponse = client.post("/movies", json=newMovie)
    assert createResponse.status_code == 201 #assert movie creation was successful
    createdMovie = createResponse.json()
    assert createdMovie["title"] == newMovie["title"]
    assert createdMovie["director"] == newMovie["director"]
    assert createdMovie["year"] == newMovie["year"]
    assert createdMovie["genre"] == newMovie["genre"]
    movieId = createdMovie["id"]
    
def test_DeleteMovie():
    from app.model.main import app
    client = TestClient(app)
    #first create a movie to delete
    newMovie = {
        "title": "Movie to Delete",
        "director": "Director",
        "year": 2023,
        "genre": "Genre",
        "id": 5678
    }   
    createResponse = client.post("/movies", json=newMovie)
    assert createResponse.status_code == 201
    createdMovie = createResponse.json()
    movieId = createdMovie["id"]
    #now delete the movie
    deleteResponse = client.delete(f"/movies/{movieId}")
    assert deleteResponse.status_code == 204 #assert deletion was successful
    #verify the movie is deleted
    getResponse = client.get(f"/movies/{movieId}")
    assert getResponse.status_code == 404 #assert that the movie is not found after deletion
    
