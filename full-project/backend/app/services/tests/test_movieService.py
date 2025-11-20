import pytest
from fastapi import HTTPException
from app.services import movieService
from app.schemas.movie import MovieCreate, MovieUpdate
from datetime import date

# Mock data for testing movie service
sampleMovies = [
    {
        "id": 1,
        "title": "Avengers Endgame",
        "movieIMDbRating": 8.4,
        "movieGenres": ["Action", "Adventure"],
        "directors": ["Russo Brothers"],
        "mainStars": ["Robert Downey Jr."],
        "description": "Epic finale of Marvel saga.",
        "datePublished": "2019-04-26",
        "duration": 181,
    },
    {
        "id": 2,
        "title": "Inception",
        "movieIMDbRating": 8.8,
        "movieGenres": ["Sci-Fi", "Thriller"],
        "directors": ["Christopher Nolan"],
        "mainStars": ["Leonardo DiCaprio"],
        "description": "Dream within a dream.",
        "datePublished": "2010-07-16",
        "duration": 148,
    },
]


@pytest.fixture(autouse=True)
def mockRepo(monkeypatch):
    # Automatically mock loadAll/saveAll for all tests
    monkeypatch.setattr(movieService, "loadAll", lambda: sampleMovies.copy())
    monkeypatch.setattr(movieService, "saveAll", lambda data: None)



def test_list_movies():
    movies = movieService.listMovies()
    assert len(movies) == 2
    assert movies[0].title == "Avengers Endgame"


def test_get_movie_by_id_success():
    movie = movieService.getMovieById(1)
    assert movie.title == "Avengers Endgame"


def test_get_movie_by_id_not_found():
    with pytest.raises(HTTPException) as excInfo:
        movieService.getMovieById(999)
    assert excInfo.value.status_code == 404
    assert "Movie not found" in excInfo.value.detail


def test_search_movie_title_match():
    results = movieService.searchMovie("Inception")
    assert len(results) == 1
    assert results[0].title == "Inception"


def test_search_movie_partial_match():
    results = movieService.searchMovie("Avengers")
    assert len(results) == 1
    assert results[0].title == "Avengers Endgame"


def test_search_movie_no_match():
    results = movieService.searchMovie("UnknownTitle")
    assert results == []


def test_delete_movie_removes_correct_id(monkeypatch):
    captured = {}

    def fakeSaveAll(data):
        
        captured["saved"] = data

    monkeypatch.setattr(movieService, "saveAll", fakeSaveAll)

    movieService.deleteMovie(1)

    assert all(savedMovie["id"] != 1 for savedMovie in captured["saved"])


def test_create_movie():
    
    movieService.loadAll = lambda: sampleMovies.copy()
    savedMovies: list = []

    def fakeSaveAll(movieDataList):
        
        savedMovies.extend(movieDataList)

    movieService.saveAll = fakeSaveAll

    payload = MovieCreate(
        title="Testing Movie",
        movieIMDbRating=9.0,
        movieGenres=["Action", "Test"],
        directors=["Test Director"],
        mainStars=["Test Star"],
        description="Just a test movie.",
        datePublished="2024-01-01",
        duration=120,
    )

    newMovie = movieService.createMovie(payload)

    # assertions
    assert newMovie.title == "Testing Movie"
    assert newMovie.datePublished == date(2024, 1, 1)
    assert len(savedMovies) == 3
    assert any(savedMovie["title"] == "Testing Movie" for savedMovie in savedMovies)


def test_update_movie():
    movieService.loadAll = lambda: sampleMovies.copy()
    savedMovies: list = []

    def fakeSaveAll(movieDataList):
        savedMovies.extend(movieDataList)

    movieService.saveAll = fakeSaveAll

    payload = MovieUpdate(title="Updated Title", duration=190)
    updatedMovie = movieService.updateMovie(1, payload)

    # assertions
    assert updatedMovie.title == "Updated Title"
    assert updatedMovie.duration == 190

    assert len(savedMovies) == 2
    assert savedMovies[0]["title"] == "Updated Title"


def test_get_movie_by_filter_genre():
    results = movieService.getMovieByFilter(genre="Action")
    assert len(results) == 1
    assert results[0].title == "Avengers Endgame"


def test_get_movie_by_filter_year():
    results = movieService.getMovieByFilter(year=2010)
    assert len(results) == 1
    assert results[0].title == "Inception"


def test_get_movie_by_filter_director():
    results = movieService.getMovieByFilter(director="Nolan")
    assert len(results) == 1
    assert results[0].title == "Inception"


def test_get_movie_by_filter_star():
    results = movieService.getMovieByFilter(star="Robert")
    assert len(results) == 1
    assert results[0].title == "Avengers Endgame"
