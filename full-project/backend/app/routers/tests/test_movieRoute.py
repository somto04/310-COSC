"""
Integration and Unit Tests for Movie Router

This file contains:
1. Unit tests - Test individual service functions in isolation
2. Integration tests - Test the API endpoints with FastAPI TestClient
"""

import pytest #for test framework
from fastapi.testclient import TestClient #to simulate http requests
from fastapi import FastAPI #to create a test app
from unittest.mock import patch, MagicMock #to mock dependencies
from app.routers.movieRoute import router #testing the movie router
from app.schemas.movie import Movie, MovieCreate, MovieUpdate #data models

# SETUP & FIXTURES

# this method creates a FastAPI app instance for testing
@pytest.fixture
def app():
    """Create a FastAPI app instance for testing"""
    app = FastAPI()
    app.include_router(router)
    return app

# creates a test client for making HTTP requests to the app
@pytest.fixture
def client(app):
    """Create a test client for making HTTP requests"""
    return TestClient(app)

# sample movie to use in tests
@pytest.fixture
def sample_movie_data():
    """Sample movie data for testing"""
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

# sample list of movies for testing
@pytest.fixture
def sample_movies_list(sample_movie_data):
    """Sample list of movies for testing"""
    return [
        sample_movie_data,
        {
            "id": 2,
            "title": "The Matrix",
            "movieIMDbRating": 8.7,
            "movieGenres": ["Action", "Sci-Fi"],
            "directors": ["Lana Wachowski", "Lilly Wachowski"],
            "mainStars": ["Keanu Reeves", "Laurence Fishburne"],
            "description": "A computer hacker learns about reality",
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
            "description": "The aging patriarch of an organized crime dynasty",
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
            "description": "The lives of two mob hitmen, a boxer, and others intertwine",
            "datePublished": "1994-10-14",
            "duration": 154
        }
    ]


# ============================================================================
# UNIT TESTS - Testing service functions in isolation
# ============================================================================

class TestMovieServiceUnit:
    """Unit tests for movie service functions"""
    
    @patch('app.services.movieService.loadAll')
    def test_list_movies_returns_all_movies(self, mock_load, sample_movies_list):
        """Test that listMovies returns all movies from database"""
        # Arrange - set up the mock to return sample data
        mock_load.return_value = sample_movies_list
        from app.services.movieService import listMovies
        
        # Act - call the function
        result = listMovies()
        
        # Assert - verify results
        assert len(result) == 4
        assert result[0].title == "Inception"
        assert result[1].title == "The Matrix"
        mock_load.assert_called_once()  # Verify loadAll was called
    
    
    @patch('app.services.movieService.saveAll')
    @patch('app.services.movieService.loadAll')
    def test_create_movie_generates_new_id(self, mock_load, mock_save, sample_movies_list):
        """Test that createMovie generates the next sequential ID"""
        # Arrange
        mock_load.return_value = sample_movies_list
        from app.services.movieService import createMovie
        
        new_movie_data = MovieCreate(
            title="Interstellar",
            movieIMDbRating=8.6,
            movieGenres=["Adventure", "Drama", "Sci-Fi"],
            directors=["Christopher Nolan"],
            mainStars=["Matthew McConaughey"],
            description="A team of explorers travel through a wormhole",
            datePublished="2014-11-07",
            duration=169
        )
        
        # Act
        result = createMovie(new_movie_data)
        
        # Assert
        assert result.id == 5  # Should be max(1, 2, 3, 4) + 1
        assert result.title == "Interstellar"
        mock_save.assert_called_once()  # Verify saveAll was called
    
    
    @patch('app.services.movieService.loadAll')
    def test_get_movie_by_id_success(self, mock_load, sample_movie_data):
        """Test getting a movie by ID when it exists"""
        # Arrange
        mock_load.return_value = [sample_movie_data]
        from app.services.movieService import getMovieById
        
        # Act
        result = getMovieById(1)
        
        # Assert
        assert result.id == 1
        assert result.title == "Inception"
    
    
    @patch('app.services.movieService.loadAll')
    def test_get_movie_by_id_not_found(self, mock_load, sample_movie_data):
        """Test getting a movie by ID when it doesn't exist raises 404"""
        # Arrange
        mock_load.return_value = [sample_movie_data]
        from app.services.movieService import getMovieById
        from fastapi import HTTPException
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            getMovieById(999)  # Non-existent ID
        
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Movie not found"
    
    
    @patch('app.services.movieService.saveAll')
    @patch('app.services.movieService.loadAll')
    def test_update_movie_success(self, mock_load, mock_save, sample_movie_data):
        """Test updating a movie successfully"""
        # Arrange
        mock_load.return_value = [sample_movie_data]
        from app.services.movieService import updateMovie
        
        update_data = MovieUpdate(
            title="Inception (Director's Cut)",
            movieIMDbRating=9.0
        )
        
        # Act
        result = updateMovie(1, update_data)
        
        # Assert
        assert result.title == "Inception (Director's Cut)"
        assert result.movieIMDbRating == 9.0
        assert result.duration == 148  # Unchanged field
        mock_save.assert_called_once()
    
    
    @patch('app.services.movieService.saveAll')
    @patch('app.services.movieService.loadAll')
    def test_delete_movie_success(self, mock_load, mock_save, sample_movies_list):
        """Test deleting a movie successfully"""
        # Arrange
        mock_load.return_value = sample_movies_list
        from app.services.movieService import deleteMovie
        
        # Act
        deleteMovie(1)
        
        # Assert
        # Verify saveAll was called with filtered list (without movie id=1)
        mock_save.assert_called_once()
        saved_movies = mock_save.call_args[0][0]
        assert len(saved_movies) == 3
        assert saved_movies[0]["id"] == 2
    
    
    @patch('app.services.movieService.loadAll')
    def test_search_movie_by_title(self, mock_load, sample_movies_list):
        """Test searching movies by title"""
        # Arrange
        mock_load.return_value = sample_movies_list
        from app.services.movieService import searchMovie
        
        # Act
        results = searchMovie("inception")
        
        # Assert
        assert len(results) == 1
        assert results[0]["title"] == "Inception"
    
    
    @patch('app.services.movieService.loadAll')
    def test_search_movie_by_genre(self, mock_load, sample_movies_list):
        """Test searching movies by genre (case-insensitive)"""
        # Arrange
        mock_load.return_value = sample_movies_list
        from app.services.movieService import searchMovie
        
        # Act - search for "action" which should match both movies
        results = searchMovie("action")
        
        # Assert
        assert len(results) == 2  # Both movies have Action genre
    
    
    @patch('app.services.movieService.loadAll')
    def test_search_movie_empty_query(self, mock_load, sample_movies_list):
        """Test searching with empty query returns empty list"""
        # Arrange
        mock_load.return_value = sample_movies_list
        from app.services.movieService import searchMovie
        
        # Act
        results = searchMovie("")
        
        # Assert
        assert len(results) == 0


# ============================================================================
# INTEGRATION TESTS - Testing API endpoints with HTTP requests
# ============================================================================

class TestMovieRouterIntegration:
    """Integration tests for movie API endpoints"""
    
    @patch('app.services.movieService.listMovies')
    def test_get_all_movies_endpoint(self, mock_list, client, sample_movies_list):
        """Test GET /movies returns all movies"""
        # Arrange
        mock_list.return_value = [Movie(**m) for m in sample_movies_list]
        
        # Act
        response = client.get("/movies")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 4
        assert data[0]["title"] == "Inception"
        assert data[1]["title"] == "The Matrix"
    
    
    @patch('app.services.movieService.getMovieById')
    def test_get_movie_by_id_endpoint(self, mock_get, client, sample_movie_data):
        """Test GET /movies/{id} returns specific movie"""
        # Arrange
        mock_get.return_value = Movie(**sample_movie_data)
        
        # Act
        response = client.get("/movies/1")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["title"] == "Inception"
        assert data["movieIMDbRating"] == 8.8
        mock_get.assert_called_once_with(1)
    
    
    @patch('app.services.movieService.getMovieById')
    def test_get_movie_by_id_not_found(self, mock_get, client):
        """Test GET /movies/{id} with non-existent ID returns 404"""
        # Arrange
        from fastapi import HTTPException
        mock_get.side_effect = HTTPException(status_code=404, detail="Movie not found")
        
        # Act
        response = client.get("/movies/999")
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Movie not found"
    
    
    @patch('app.services.movieService.searchMovie')
    def test_search_movies_with_query(self, mock_search, client, sample_movie_data):
        """Test GET /movies/search?q=keyword returns matching movies"""
        # Arrange
        mock_search.return_value = [sample_movie_data]
        
        # Act
        response = client.get("/movies/search?q=inception")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Inception"
        mock_search.assert_called_once_with("inception")
    
    
    @patch('app.services.movieService.searchMovie')
    def test_search_movies_no_results(self, mock_search, client):
        """Test search with no results returns 404"""
        # Arrange
        mock_search.return_value = []
        
        # Act
        response = client.get("/movies/search?q=nonexistent")
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Movie not found"


# ============================================================================
# EDGE CASE TESTS
# ============================================================================

class TestMovieEdgeCases:
    """Test edge cases and error scenarios"""
    
    @patch('app.services.movieService.loadAll')
    def test_search_with_case_insensitive(self, mock_load, sample_movies_list):
        """Test search is case-insensitive"""
        # Arrange
        mock_load.return_value = sample_movies_list
        from app.services.movieService import searchMovie
        
        # Act - search with lowercase
        results = searchMovie("action")
        
        # Assert - should match "Action" genre
        assert len(results) == 2  # Both movies have Action genre
    
    
    @patch('app.services.movieService.loadAll')
    def test_get_movie_with_string_id_converts_to_int(self, mock_load, sample_movie_data):
        """Test that service handles string IDs by converting to int"""
        # Arrange
        mock_load.return_value = [sample_movie_data]
        from app.services.movieService import getMovieById
        
        # Act
        result = getMovieById(1)  # Even though route passes string, service converts
        
        # Assert
        assert result.id == 1
    
    
    @patch('app.services.movieService.saveAll') #@patch() means we are mocking the saveAll function from movieService
    @patch('app.services.movieService.loadAll')
    def test_update_movie_partial_update(self, mock_load, mock_save, sample_movie_data):
        """Test updating only some fields leaves others unchanged"""
        # Arrange
        mock_load.return_value = [sample_movie_data]
        from app.services.movieService import updateMovie
        
        # Act - only update rating
        update_data = MovieUpdate(movieIMDbRating=9.0)
        result = updateMovie(1, update_data)
        
        # Assert
        assert result.movieIMDbRating == 9.0
        assert result.title == "Inception"  # Unchanged
        assert result.duration == 148  # Unchanged


# HOW TO RUN THESE TESTS
"""
To run all tests:
    pytest app/routers/tests/test_movieRoute.py -v

To run only unit tests:
    pytest app/routers/tests/test_movieRoute.py::TestMovieServiceUnit -v

To run only integration tests:
    pytest app/routers/tests/test_movieRoute.py::TestMovieRouterIntegration -v

To run a specific test:
    pytest app/routers/tests/test_movieRoute.py::TestMovieServiceUnit::test_list_movies_returns_all_movies -v

To see print statements:
    pytest app/routers/tests/test_movieRoute.py -v -s

To see coverage:
    pytest app/routers/tests/test_movieRoute.py --cov=app.services.movieService --cov=app.routers.movieRoute
"""