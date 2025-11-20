import pytest
from unittest.mock import patch, MagicMock

from ..tmdbService import getMovieDetails, getRecommendations
from ..tmdbSchema import TMDbMovie, TMDbRecommendation


@patch("app.externalAPI.tmdbService.requests.get")
def test_get_movie_details_success(mock_get):
    """getMovieDetails returns a TMDbMovie model when API returns results."""
    
    # Fake TMDb API response
    fake_json = {
        "results": [
            {
                "id": 123,
                "title": "Inception",
                "poster_path": "/poster.jpg",
                "overview": "A dream within a dream.",
                "vote_average": 8.8
            }
        ]
    }

    # Configure the mocked API call
    mock_response = MagicMock()
    mock_response.json.return_value = fake_json
    mock_get.return_value = mock_response

    movie = getMovieDetails("Inception")

    assert isinstance(movie, TMDbMovie)
    assert movie.id == 123
    assert movie.title == "Inception"
    assert movie.poster.endswith("/poster.jpg")
    assert movie.overview == "A dream within a dream."
    assert movie.rating == 8.8


@patch("app.externalAPI.tmdbService.requests.get")
def test_get_movie_details_no_results(mock_get):
    """getMovieDetails returns None when API returns no matches."""

    mock_response = MagicMock()
    mock_response.json.return_value = {"results": []}
    mock_get.return_value = mock_response

    movie = getMovieDetails("Unknown Title")
    assert movie is None



@patch("app.externalAPI.tmdbService.requests.get")
def test_get_recommendations(mock_get):
    """getRecommendations returns a list of TMDbRecommendation models."""

    fake_json = {
        "results": [
            {
                "id": 100,
                "title": "Dunkirk",
                "poster_path": "/dunkirk.jpg",
                "vote_average": 7.9
            },
            {
                "id": 101,
                "title": "Tenet",
                "poster_path": "/tenet.jpg",
                "vote_average": 7.5
            }
        ]
    }

    mock_response = MagicMock()
    mock_response.json.return_value = fake_json
    mock_get.return_value = mock_response

    recs = getRecommendations(123)
    
    assert len(recs) == 2
    assert isinstance(recs[0], TMDbRecommendation)
    assert recs[0].title == "Dunkirk"
    assert recs[1].title == "Tenet"
    assert recs[0].rating == 7.9
    assert recs[1].poster.endswith("/tenet.jpg")
