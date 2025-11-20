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
def sample_movie_data():
    return {
        "id": 1,
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
def sample_movies_list(sample_movie_data):
    return [
        sample_movie_data,
        {
            "id": 2,
            "title": "The Matrix",
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
    def test_list_movies_returns_all_movies(self, mock_load, sample_movies_list):
        mock_load.return_value = sample_movies_list
        from app.services.movieService import listMovies

        result = listMovies()

        assert len(result) == 4
        assert result[0].title == "Inception"
        assert result[1].title == "The Matrix"

    @patch('app.services.movieService.saveAll')
    @patch('app.services.movieService.loadAll')
    def test_create_movie_generates_new_id(self, mock_load, mock_save, sample_movies_list):
        mock_load.return_value = sample_movies_list
        from app.services.movieService import createMovie

        new_movie_data = MovieCreate(
            title="Interstellar",
            movieIMDbRating=8.6,
            movieGenres=["Adventure", "Drama", "Sci-Fi"],
            directors=["Christopher Nolan"],
            mainStars=["Matthew McConaughey"],
            description="A wormhole journey",
            datePublished="2014-11-07",
            duration=169
        )

        result = createMovie(new_movie_data)

        assert result.id == 5
        assert result.title == "Interstellar"
        mock_save.assert_called_once()

    @patch('app.services.movieService.loadAll')
    def test_get_movie_by_id_success(self, mock_load, sample_movie_data):
        mock_load.return_value = [sample_movie_data]
        from app.services.movieService import getMovieById

        result = getMovieById(1)

        assert result.id == 1
        assert result.title == "Inception"

    @patch('app.services.movieService.loadAll')
    def test_get_movie_by_id_not_found(self, mock_load, sample_movie_data):
        mock_load.return_value = [sample_movie_data]
        from app.services.movieService import getMovieById
        from fastapi import HTTPException

        with pytest.raises(HTTPException):
            getMovieById(999)

    @patch('app.services.movieService.saveAll')
    @patch('app.services.movieService.loadAll')
    def test_update_movie_success(self, mock_load, mock_save, sample_movie_data):
        mock_load.return_value = [sample_movie_data]
        from app.services.movieService import updateMovie

        update_data = MovieUpdate(title="Inception (Director's Cut)", movieIMDbRating=9.0)

        result = updateMovie(1, update_data)

        assert result.title == "Inception (Director's Cut)"
        assert result.movieIMDbRating == Decimal("9.0")
        assert result.duration == 148
        mock_save.assert_called_once()

    @patch('app.services.movieService.loadAll')
    def test_search_movie_by_title(self, mock_load, sample_movies_list):
        mock_load.return_value = sample_movies_list
        from app.services.movieService import searchMovie

        results = searchMovie("inception")

        assert len(results) == 1
        assert results[0].title == "Inception"

    @patch('app.services.movieService.loadAll')
    def test_search_movie_by_genre(self, mock_load, sample_movies_list):
        mock_load.return_value = sample_movies_list
        from app.services.movieService import searchMovie

        results = searchMovie("action")

        assert len(results) == 2

    @patch('app.services.movieService.loadAll')
    def test_search_movie_empty_query(self, mock_load, sample_movies_list):
        mock_load.return_value = sample_movies_list
        from app.services.movieService import searchMovie

        results = searchMovie("")

        assert results == []



# INTEGRATION TESTS

class TestMovieRouterIntegration:

    @patch('app.routers.movieRoute.listMovies')
    def test_get_all_movies_endpoint(self, mock_list, client, sample_movies_list):
        mock_list.return_value = [Movie(**m) for m in sample_movies_list]

        response = client.get("/movies")
        data = response.json()

        assert response.status_code == 200
        assert len(data) == 4
        assert data[0]["title"] == "Inception"

    @patch('app.routers.movieRoute.getMovieById')
    def test_get_movie_by_id_endpoint(self, mock_get, client, sample_movie_data):
        mock_get.return_value = Movie(**sample_movie_data)

        response = client.get("/movies/1")
        data = response.json()

        assert response.status_code == 200
        assert data["id"] == 1
        assert data["title"] == "Inception"

    @patch('app.routers.movieRoute.getMovieById')
    def test_get_movie_by_id_not_found(self, mock_get, client):
        from fastapi import HTTPException
        mock_get.side_effect = HTTPException(status_code=404, detail="Movie not found")

        response = client.get("/movies/999")

        assert response.status_code == 404
        assert response.json()["detail"] == "Movie not found"

    @patch('app.routers.movieRoute.searchMovie')
    def test_search_movies_with_query(self, mock_search, client, sample_movie_data):
        mock_search.return_value = [Movie(**sample_movie_data)]

        response = client.get("/movies/search?query=inception")
        data = response.json()

        assert response.status_code == 200
        assert len(data) == 1
        assert data[0]["title"] == "Inception"
        mock_search.assert_called_once_with("inception")

    @patch('app.routers.movieRoute.searchMovie')
    def test_search_movies_no_results(self, mock_search, client):
        mock_search.return_value = []

        response = client.get("/movies/search?query=none")
        assert response.status_code == 404
        assert response.json()["detail"] == "Movie not found"


# EDGE CASE TESTS

class TestMovieEdgeCases:

    @patch('app.services.movieService.loadAll')
    def test_search_case_insensitive(self, mock_load, sample_movies_list):
        mock_load.return_value = sample_movies_list
        from app.services.movieService import searchMovie

        results = searchMovie("ACTION")
        assert len(results) == 2

    @patch('app.services.movieService.loadAll')
    def test_get_movie_id_string(self, mock_load, sample_movie_data):
        mock_load.return_value = [sample_movie_data]
        from app.services.movieService import getMovieById

        result = getMovieById("1")
        assert result.id == 1

    @patch('app.services.movieService.saveAll')
    @patch('app.services.movieService.loadAll')
    def test_partial_update(self, mock_load, mock_save, sample_movie_data):
        mock_load.return_value = [sample_movie_data]
        from app.services.movieService import updateMovie

        update_data = MovieUpdate(movieIMDbRating=9.0)
        result = updateMovie(1, update_data)

        assert result.movieIMDbRating == Decimal("9.0")
        assert result.title == "Inception"
