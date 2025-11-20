import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from fastapi import FastAPI

from ..tmdbRouter import router
from ..tmdbSchema import TMDbMovie, TMDbRecommendation


@pytest.fixture
def app():
    """Create a FastAPI instance with TMDb router included."""
    app = FastAPI()
    app.include_router(router)
    return app


@pytest.fixture
def client(app):
    """Client used for making test HTTP requests."""
    return TestClient(app)



@patch("app.externalAPI.tmdbRouter.getMovieDetails")
def test_tmdbDetailsSuccess(mock_get_details, client):
    """Successfully returns movie details."""

    fakeMovie = TMDbMovie(
        id=123,
        title="Inception",
        poster="https://image.tmdb.org/t/p/w500/poster.jpg",
        overview="A dream within a dream.",
        rating=8.8
    )

    mock_get_details.return_value = fakeMovie

    response = client.get("/tmdb/details/Inception")

    assert response.status_code == 200
    data = response.json()

    assert data["id"] == 123
    assert data["title"] == "Inception"
    assert data["rating"] == 8.8

    mock_get_details.assert_called_once_with("Inception")


@patch("app.externalAPI.tmdbRouter.getMovieDetails")
def test_tmdbDetailsNotFound(mock_get_details, client):
    """If TMDb returns None, API should return 404."""
    
    mock_get_details.return_value = None

    response = client.get("/tmdb/details/UnknownMovie")

    assert response.status_code == 404
    assert response.json()["detail"] == "Movie not found"


# ---------------------------------
# TEST /tmdb/recommendations/{movie_id}
# ---------------------------------

@patch("app.externalAPI.tmdbRouter.getRecommendations")
def test_tmdbRecommendationsSuccess(mock_get_recs, client):
    """Successfully returns a list of recommendations."""

    fakeRecs = [
        TMDbRecommendation(
            id=1,
            title="Dunkirk",
            poster="https://image.tmdb.org/t/p/w500/dunkirk.jpg",
            rating=7.9
        ),
        TMDbRecommendation(
            id=2,
            title="Tenet",
            poster="https://image.tmdb.org/t/p/w500/tenet.jpg",
            rating=7.5
        )
    ]

    mock_get_recs.return_value = fakeRecs

    response = client.get("/tmdb/recommendations/123")

    assert response.status_code == 200

    data = response.json()
    assert len(data) == 2

    assert data[0]["title"] == "Dunkirk"
    assert data[1]["title"] == "Tenet"

    mock_get_recs.assert_called_once_with(123)


@patch("app.externalAPI.tmdbRouter.getRecommendations")
def test_tmdbRecommendationsEmpty(mock_get_recs, client):
    """Even if TMDb returns empty list, should return 200 + empty list."""
    
    mock_get_recs.return_value = []

    response = client.get("/tmdb/recommendations/999")

    assert response.status_code == 200
    assert response.json() == []

    mock_get_recs.assert_called_once_with(999)
