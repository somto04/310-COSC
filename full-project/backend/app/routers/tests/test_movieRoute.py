"""
Integration and Unit Tests for Movie Router

This file contains:
1. Unit tests - Test individual service functions in isolation
2. Integration tests - Test the API endpoints with FastAPI TestClient
"""

from decimal import Decimal
import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from unittest.mock import patch
from app.routers.movieRoute import router
from app.schemas.movie import Movie, MovieCreate, MovieUpdate


import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from unittest.mock import patch
from app.routers.movieRoute import router
from app.schemas.movie import Movie, MovieCreate, MovieUpdate


@pytest.fixture
def app():
    app = FastAPI()
    app.include_router(router)
    return app


@pytest.fixture
def client(app):
    return TestClient(app)


@pytest.fixture
def sampleMovieData():
    return {
        "id": 1,
        "tmdbId": 123456,
        "title": "Inception",
        "movieIMDbRating": 8.8,
        "movieGenres": ["Action", "Sci-Fi", "Thriller"],
        "directors": ["Christopher Nolan"],
        "mainStars": ["Leonardo DiCaprio", "Tom Hardy"],
        "description": "A thief who steals corporate secrets",
        "datePublished": "2010-07-16",
        "duration": 148
    }


@pytest.fixture
def sampleMoviesList(sampleMovieData):
    return [
        sampleMovieData,
        {
            "id": 2,
            "title": "The Matrix",
            "tmdbId": 654321,
            "movieIMDbRating": 8.7,
            "movieGenres": ["Action", "Sci-Fi"],
            "directors": ["Lana Wachowski", "Lilly Wachowski"],
            "mainStars": ["Keanu Reeves", "Laurence Fishburne"],
            "description": "A hacker discovers reality is a simulation",
            "datePublished": "1999-03-31",
            "duration": 136
        },
        {
            "id": 3,
            "title": "The Godfather",
            "tmdbId": 111222,
            "movieIMDbRating": 9.2,
            "movieGenres": ["Crime", "Drama"],
            "directors": ["Francis Ford Coppola"],
            "mainStars": ["Marlon Brando", "Al Pacino"],
            "description": "A mafia family's power struggles",
            "datePublished": "1972-03-24",
            "duration": 175
        },
        {
            "id": 4,
            "tmdbId": 333444,
            "title": "Pulp Fiction",
            "movieIMDbRating": 8.9,
            "movieGenres": ["Crime", "Drama"],
            "directors": ["Quentin Tarantino"],
            "mainStars": ["John Travolta", "Uma Thurman"],
            "description": "Interconnected crime stories",
            "datePublished": "1994-10-14",
            "duration": 154
        }
    ]


# UNIT TESTS

class TestMovieServiceUnit:

    @patch('app.services.movieService.loadAll')
    def test_listMoviesReturnsAllMovies(self, mockLoad, sampleMoviesList):
        mockLoad.return_value = sampleMoviesList
        from app.services.movieService import listMovies

        result = listMovies()

        assert len(result) == 4
        assert result[0].title == "Inception"
        assert result[1].title == "The Matrix"

    @patch('app.services.movieService.saveAll')
    @patch('app.services.movieService.loadAll')
    def test_createMovieGeneratesNewId(self, mockLoad, mockSave, sampleMoviesList):
        mockLoad.return_value = sampleMoviesList
        from app.services.movieService import createMovie

        newMovieData = MovieCreate(
            title="Interstellar",
            tmdbId=555666,
            movieIMDbRating=8.6,
            movieGenres=["Adventure", "Drama", "Sci-Fi"],
            directors=["Christopher Nolan"],
            mainStars=["Matthew McConaughey"],
            description="A wormhole journey",
            datePublished="2014-11-07",
            duration=169
        )

        result = createMovie(newMovieData)

        assert result.id == 5
        assert result.title == "Interstellar"
        mockSave.assert_called_once()

    @patch('app.services.movieService.loadAll')
    def test_getMovieByIdSuccess(self, mockLoad, sampleMovieData):
        mockLoad.return_value = [sampleMovieData]
        from app.services.movieService import getMovieById

        result = getMovieById(1)

        assert result.id == 1
        assert result.title == "Inception"

    @patch('app.services.movieService.loadAll')
    def test_getMovieByIdNotFound(self, mockLoad, sampleMovieData):
        mockLoad.return_value = [sampleMovieData]
        from app.services.movieService import getMovieById
        from fastapi import HTTPException

        with pytest.raises(HTTPException):
            getMovieById(999)

    @patch('app.services.movieService.saveAll')
    @patch('app.services.movieService.loadAll')
    def test_UpdateMovieSuccess(self, mockLoad, mock_save, sampleMovieData):
        mockLoad.return_value = [sampleMovieData]
        from app.services.movieService import updateMovie

        update_data = MovieUpdate(title="Inception (Director's Cut)", movieIMDbRating=9.0)

        result = updateMovie(1, update_data)

        assert result.title == "Inception (Director's Cut)"
        assert result.movieIMDbRating == Decimal("9.0")
        assert result.duration == 148
        mock_save.assert_called_once()

    @patch('app.services.movieService.loadAll')
    def test_searchMovieByTitle(self, mockLoad, sampleMoviesList):
        mockLoad.return_value = sampleMoviesList
        from app.services.movieService import searchMovie

        results = searchMovie("inception")

        assert len(results) == 1
        assert results[0].title == "Inception"

    @patch('app.services.movieService.loadAll')
    def test_SearchMovieByGenre(self, mockLoad, sampleMoviesList):
        mockLoad.return_value = sampleMoviesList
        from app.services.movieService import searchMovie

        results = searchMovie("action")

        assert len(results) == 2

    @patch('app.services.movieService.loadAll')
    def test_searchMovieEmptyQuery(self, mockLoad, sampleMoviesList):
        mockLoad.return_value = sampleMoviesList
        from app.services.movieService import searchMovie

        results = searchMovie("")

        assert results == []



# INTEGRATION TESTS

class TestMovieRouterIntegration:

    @patch('app.routers.movieRoute.listMovies')
    def test_GetAllMoviesEndpoint(self, mockList, client, sampleMoviesList):
        mockList.return_value = [Movie(**m) for m in sampleMoviesList]

        response = client.get("/movies")
        data = response.json()

        assert response.status_code == 200
        assert len(data) == 4
        assert data[0]["title"] == "Inception"

    @patch('app.routers.movieRoute.getMovieById')
    def test_getMovieByIdEndpoint(self, mockGet, client, sampleMovieData):
        mockGet.return_value = Movie(**sampleMovieData)

        response = client.get("/movies/1")
        data = response.json()

        assert response.status_code == 200
        assert data["id"] == 1
        assert data["title"] == "Inception"

    @patch('app.routers.movieRoute.getMovieById')
    def test_getMovieByIdNotFound(self, mockGet, client):
        from fastapi import HTTPException
        mockGet.side_effect = HTTPException(status_code=404, detail="Movie not found")

        response = client.get("/movies/999")

        assert response.status_code == 404
        assert response.json()["detail"] == "Movie not found"

    @patch('app.routers.movieRoute.searchMovie')
    def test_searchMoviesWithQuery(self, mockSearch, client, sampleMovieData):
        mockSearch.return_value = [Movie(**sampleMovieData)]

        response = client.get("/movies/search?query=inception")
        data = response.json()

        assert response.status_code == 200
        assert len(data) == 1
        assert data[0]["title"] == "Inception"
        mockSearch.assert_called_once_with("inception")

    @patch('app.routers.movieRoute.searchMovie')
    def test_searchMoviesNoResults(self, mockSearch, client):
        mockSearch.return_value = []

        response = client.get("/movies/search?query=none")
        assert response.status_code == 404
        assert response.json()["detail"] == "Movie not found"


# EDGE CASE TESTS

class TestMovieEdgeCases:

    @patch('app.services.movieService.loadAll')
    def test_searchCaseInsensitive(self, mockLoad, sampleMoviesList):
        mockLoad.return_value = sampleMoviesList
        from app.services.movieService import searchMovie

        results = searchMovie("ACTION")
        assert len(results) == 2

    @patch('app.services.movieService.loadAll')
    def test_getMovieIdString(self, mockLoad, sampleMovieData):
        mockLoad.return_value = [sampleMovieData]
        from app.services.movieService import getMovieById

        result = getMovieById("1")
        assert result.id == 1

    @patch('app.services.movieService.saveAll')
    @patch('app.services.movieService.loadAll')
    def test_partialUpdate(self, mockLoad, mockSave, sampleMovieData):
        mockLoad.return_value = [sampleMovieData]
        from app.services.movieService import updateMovie

        updateData = MovieUpdate(movieIMDbRating=9.0)
        result = updateMovie(1, updateData)

        assert result.movieIMDbRating == Decimal("9.0")
        assert result.title == "Inception"
