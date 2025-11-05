import pytest
from fastapi import HTTPException
from app.services import movieService
from app.schemas.movie import MovieCreate, MovieUpdate

#Mock data for testing movie service
sample_movies = [
    {
        "id": 1,
        "title": "Avengers Endgame",
        "movieIMDbRating": 8.4,
        "movieGenres": ["Action", "Adventure"],
        "directors": ["Russo Brothers"],
        "mainStars": ["Robert Downey Jr."],
        "description": "Epic finale of Marvel saga.",
        "datePublished": "2019-04-26",
        "duration": 181
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
        "duration": 148
    }
]

@pytest.fixture(autouse=True)
def mock_repo(monkeypatch):
    #Automatically mock loadAll/saveAll for all tests
    monkeypatch.setattr(movieService, "loadAll", lambda: sample_movies.copy())
    monkeypatch.setattr(movieService, "saveAll", lambda data: None)

# this tests the listMovies function to ensure it returns movies currently in the database
def test_list_movies():
    movies = movieService.listMovies()
    assert len(movies) == 2
    assert movies[0].title == "Avengers Endgame"

# this tests that getMovieById returns the correct movie
def test_get_movie_by_id_success():
    movie = movieService.getMovieById("1")
    assert movie.title == "Avengers Endgame"

# this tests that getMovieById raises an exception for a non-existent movie
def test_get_movie_by_id_not_found():
    with pytest.raises(HTTPException) as e:
        movieService.getMovieById("999")
    assert e.value.status_code == 404
    assert "Movie not found" in e.value.detail

# this tests that searchMovie returns correct results based on a string query
def test_search_movie_title_match():
    results = movieService.searchMovie("Inception")
    assert len(results) == 1
    assert results[0]["title"] == "Inception"

# this tests that searchMovie returns correct results for partial matches
def test_search_movie_partial_match():
    results = movieService.searchMovie("Avengers")
    assert len(results) == 1
    assert results[0]["title"] == "Avengers Endgame"

# this tests that searchMovie returns an empty list when there are no matches
def test_search_movie_no_match():
    results = movieService.searchMovie("UnknownTitle")
    assert results == []

# this tests that deleteMovie removes the correct movie by id
def test_delete_movie_removes_correct_id(monkeypatch):
    captured = {}

    def fake_saveAll(data):
        captured["saved"] = data

    monkeypatch.setattr(movieService, "saveAll", fake_saveAll)
    movieService.deleteMovie("1")
    assert all(m["id"] != "1" for m in captured["saved"])

# this tests that createMovie adds a new movie correctly based on our schema
def test_create_movie():
    # mock loadAll and saveAll
    movieService.loadAll = lambda: sample_movies.copy()
    saved_movies = []
    movieService.saveAll = lambda movies: saved_movies.extend(movies)

    payload = MovieCreate(
        title="Testing Movie",
        movieIMDbRating=9.0,
        movieGenres=["Action", "Test"],
        directors=["Test Director"],
        mainStars=["Test Star"],
        description="Just a test movie.",
        datePublished="2024-01-01",
        duration=120
    )

    new_movie = movieService.createMovie(payload)

    #assertions
    assert new_movie.title == "Testing Movie"
    assert new_movie.datePublished == "2024-01-01"
    assert len(saved_movies) == 3 
    assert any(m["title"] == "Testing Movie" for m in saved_movies)

# this tests that updateMovie modifies an existing movie correctly
def test_update_movie():
    movieService.loadAll = lambda: sample_movies.copy()
    saved_movies = []
    movieService.saveAll = lambda movies: saved_movies.extend(movies)

    payload = MovieUpdate(title="Updated Title", duration=190)
    updated_movie = movieService.updateMovie("1", payload)

    #assertions
    assert updated_movie.title == "Updated Title"
    assert updated_movie.duration == 190

    # make sure it saved correctly
    assert len(saved_movies) == 2
    assert saved_movies[0]["title"] == "Updated Title"

#these tests verify filtering functionality in getMovieByFilter
def test_get_movie_by_filter_genre():
    results = movieService.getMovieByFilter(genre="Action")
    assert len(results) == 1
    assert results[0]["title"] == "Avengers Endgame"

def test_get_movie_by_filter_year():
    results = movieService.getMovieByFilter(year=2010)
    assert len(results) == 1
    assert results[0]["title"] == "Inception"

def test_get_movie_by_filter_director():
    results = movieService.getMovieByFilter(director="Nolan")
    assert len(results) == 1
    assert results[0]["title"] == "Inception"

def test_get_movie_by_filter_star():
    results = movieService.getMovieByFilter(star="Robert")
    assert len(results) == 1
    assert results[0]["title"] == "Avengers Endgame"