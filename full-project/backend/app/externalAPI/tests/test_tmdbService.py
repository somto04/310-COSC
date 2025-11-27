import pytest
from unittest.mock import patch, MagicMock

from ..tmdbService import (
    getMovieDetailsByName,
    getMovieDetailsById,
    getRecommendationsById,
    getRecommendationsByName
)
from ..tmdbSchema import TMDbMovie, TMDbRecommendation

@patch("app.externalAPI.tmdbService.requests.get")
def test_getMovieDetailsByNameSuccess(mockGet):
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

    mockResponse = MagicMock()
    mockResponse.json.return_value = fakeJson
    mockGet.return_value = mockResponse

    movie = getMovieDetailsByName("Inception")

    assert isinstance(movie, TMDbMovie)
    assert movie.id == 123
    assert movie.title == "Inception"
    assert movie.poster.endswith("/poster.jpg")
    assert movie.overview == "A dream within a dream."
    assert movie.rating == 8.8

@patch("app.externalAPI.tmdbService.requests.get")
def test_getMovieDetailsByNameNoResults(mockGet):
    mockResponse = MagicMock()
    mockResponse.json.return_value = {"results": []}
    mockGet.return_value = mockResponse

    movie = getMovieDetailsByName("Unknown Title")
    assert movie is None

@patch("app.externalAPI.tmdbService.requests.get")
def test_getMovieDetailsByIdSuccess(mockGet):
    fakeJson = {
        "id": 999,
        "title": "Avatar",
        "poster_path": "/avatar.jpg",
        "overview": "Space people go blue.",
        "vote_average": 7.8
    }

    mockResponse = MagicMock()
    mockResponse.json.return_value = fakeJson
    mockGet.return_value = mockResponse

    movie = getMovieDetailsById(999)

    assert isinstance(movie, TMDbMovie)
    assert movie.id == 999
    assert movie.title == "Avatar"
    assert movie.poster.endswith("/avatar.jpg")
    assert movie.rating == 7.8

@patch("app.externalAPI.tmdbService.requests.get")
def test_getRecommendationsIdSuccess(mockGet):
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

    recs = getRecommendationsById(123)

    assert len(recs) == 2
    assert isinstance(recs[0], TMDbRecommendation)
    assert recs[0].title == "Dunkirk"
    assert recs[1].title == "Tenet"
    assert recs[0].rating == 7.9
    assert recs[1].poster.endswith("/tenet.jpg")

@patch("app.externalAPI.tmdbService.requests.get")
def test_getRecommendationsByName_success(mockGet):
    
    fakeSearchJson = {
        "results": [
            {"id": 500} 
        ]
    }

   
    fakeRecJson = {
        "results": [
            {
                "id": 700,
                "title": "Interstellar",
                "poster_path": "/interstellar.jpg",
                "vote_average": 8.6
            }
        ]
    }

    mockResponse = MagicMock()
    mockResponse.json.side_effect = [fakeSearchJson, fakeRecJson]  
    mockGet.return_value = mockResponse

    recs = getRecommendationsByName("Inception")

    assert len(recs) == 1
    assert recs[0].title == "Interstellar"
    assert recs[0].poster.endswith("/interstellar.jpg")
    assert recs[0].rating == 8.6
