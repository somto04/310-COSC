import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from fastapi import FastAPI

from ..tmdbRouter import router
from ..tmdbSchema import TMDbMovie, TMDbRecommendation


@pytest.fixture
def app():
    app = FastAPI()
    app.include_router(router)
    return app


@pytest.fixture
def client(app):
    return TestClient(app)



@patch("app.externalAPI.tmdbRouter.getMovieDetailsByName")
def test_tmdbDetailsByNameSuccess(mockGetDetails, client):
    fakeMovie = TMDbMovie(
        id=123,
        title="Inception",
        poster="https://image.tmdb.org/t/p/w500/poster.jpg",
        overview="A dream within a dream.",
        rating=8.8
    )

    mockGetDetails.return_value = fakeMovie

    response = client.get("/tmdb/details/name/Inception")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 123
    assert data["title"] == "Inception"
    assert data["rating"] == 8.8

    mockGetDetails.assert_called_once_with("Inception")


@patch("app.externalAPI.tmdbRouter.getMovieDetailsByName")
def test_tmdbDetailsByNameNotFound(mockGetDetails, client):
    mockGetDetails.return_value = None

    response = client.get("/tmdb/details/name/UnknownMovie")

    assert response.status_code == 404
    assert response.json()["detail"] == "Movie not found"




@patch("app.externalAPI.tmdbRouter.getMovieDetailsById")
@patch("app.externalAPI.tmdbRouter.getMovieById")
def test_tmdbDetailsByIdSuccess(mockGetMovieById, mockGetDetailsById, client):
    
    mockGetMovieById.return_value = type("FakeMovie", (), {"tmdbId": 222})

   
    fakeMovie = TMDbMovie(
        id=222,
        title="Avengers",
        poster="https://image.tmdb.org/t/p/w500/avengers.jpg",
        overview="Earth's mightiest heroes.",
        rating=8.0
    )
    mockGetDetailsById.return_value = fakeMovie

    response = client.get("/tmdb/details/1")

    assert response.status_code == 200
    data = response.json()

    assert data["id"] == 222
    assert data["title"] == "Avengers"

    mockGetMovieById.assert_called_once_with(1)
    mockGetDetailsById.assert_called_once_with(222)


@patch("app.externalAPI.tmdbRouter.getMovieById")
def test_tmdbDetailsByIdMovieNotFound(mockGetMovieById, client):
    mockGetMovieById.return_value = None

    response = client.get("/tmdb/details/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Movie not found"




@patch("app.externalAPI.tmdbRouter.getRecommendationsByName")
def test_tmdbRecommendationsByNameSuccess(mockGetRecs, client):
    fakeRecs = [
        TMDbRecommendation(id=1, title="Dunkirk", poster="p1", rating=7.9),
        TMDbRecommendation(id=2, title="Tenet", poster="p2", rating=7.5),
    ]

    mockGetRecs.return_value = fakeRecs

    response = client.get("/tmdb/recommendations/name/Inception")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["title"] == "Dunkirk"
    assert data[1]["title"] == "Tenet"

    mockGetRecs.assert_called_once_with("Inception")


@patch("app.externalAPI.tmdbRouter.getRecommendationsByName")
def test_tmdbRecommendationsByNameEmpty(mockGetRecs, client):
    mockGetRecs.return_value = []

    response = client.get("/tmdb/recommendations/name/TestMovie")

    assert response.status_code == 200
    assert response.json() == []

    mockGetRecs.assert_called_once_with("TestMovie")




@patch("app.externalAPI.tmdbRouter.getRecommendationsById")
@patch("app.externalAPI.tmdbRouter.getMovieById")
def test_tmdbRecommendationsByIdSuccess(mockGetMovieById, mockGetRecsById, client):
    mockGetMovieById.return_value = type("FakeMovie", (), {"tmdbId": 333})

    fakeRecs = [
        TMDbRecommendation(id=5, title="Movie A", poster="pA", rating=8),
        TMDbRecommendation(id=6, title="Movie B", poster="pB", rating=7),
    ]

    mockGetRecsById.return_value = fakeRecs

    response = client.get("/tmdb/recommendations/1")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

    mockGetMovieById.assert_called_once_with(1)
    mockGetRecsById.assert_called_once_with(333)


@patch("app.externalAPI.tmdbRouter.getMovieById")
def test_tmdbRecommendationsByIdMovieNotFound(mockGetMovieById, client):
    mockGetMovieById.return_value = None

    response = client.get("/tmdb/recommendations/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Movie not found"
