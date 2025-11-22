import pytest
from unittest.mock import patch, MagicMock

from ..tmdbService import getMovieDetails, getRecommendations
from ..tmdbSchema import TMDbMovie, TMDbRecommendation


@patch("app.externalAPI.tmdbService.requests.get")
def test_getMovieDetailsSuccess(mockGet):
    """getMovieDetails returns a TMDbMovie model when API returns results."""
    
    # Fake TMDb API response
    fakeJson = {
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
    mockResponse = MagicMock()
    mockResponse.json.return_value = fakeJson
    mockGet.return_value = mockResponse

    movie = getMovieDetails("Inception")

    assert isinstance(movie, TMDbMovie)
    assert movie.id == 123
    assert movie.title == "Inception"
    assert movie.poster.endswith("/poster.jpg")
    assert movie.overview == "A dream within a dream."
    assert movie.rating == 8.8


@patch("app.externalAPI.tmdbService.requests.get")
def test_getMovieDetailsNoResults(mockGet):
    """getMovieDetails returns None when API returns no matches."""

    mockResponse = MagicMock()
    mockResponse.json.return_value = {"results": []}
    mockGet.return_value = mockResponse

    movie = getMovieDetails("Unknown Title")
    assert movie is None



@patch("app.externalAPI.tmdbService.requests.get")
def test_getRecommendations(mockGet):
    """getRecommendations returns a list of TMDbRecommendation models."""

    fakeJson = {
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

    mockResponse = MagicMock()
    mockResponse.json.return_value = fakeJson
    mockGet.return_value = mockResponse

    recs = getRecommendations(123)
    
    assert len(recs) == 2
    assert isinstance(recs[0], TMDbRecommendation)
    assert recs[0].title == "Dunkirk"
    assert recs[1].title == "Tenet"
    assert recs[0].rating == 7.9
    assert recs[1].poster.endswith("/tenet.jpg")
