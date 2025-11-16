import pytest
from ..movie import Movie, MovieCreate, MovieUpdate
from datetime import date
from pydantic import ValidationError


def test_movie_valid_input():
    movie = Movie(
        id=1,
        title="Test",
        movieGenres=["Drama"],
        datePublished="2020-01-01",  # type: ignore
        duration=120,
    )
    assert movie.datePublished.year == 2020  # type: ignore


def test_movie_invalid_date():
    with pytest.raises(ValidationError):
        Movie(
            id=1,
            title="Test",
            movieGenres=["Drama"],
            datePublished="invalid-date",  # type: ignore
            duration=120,
        )


def test_movie_aliases():
    movie = Movie(
        id=1,
        movieGenre=["Action"],  # legacy key # type: ignore
        movieName="Thing",  # type: ignore
        duration=100,
    )
    assert movie.movieGenres == ["Action"]


def test_default_factory_lists():
    m1 = MovieCreate(title="Bullet Train", movieGenres=["Action"], duration=120)
    m2 = MovieCreate(title="Oppenheimer", movieGenres=["Drama"], duration=180)

    assert m1.directors == []
    assert m2.directors == []
    assert m1.directors is not m2.directors  # ensure fresh list each time


def test_extract_year_from_date_pipeline():
    payload = MovieCreate(
        title="JuJutsu Kaisen 0",
        movieGenres=["Animation"],
        datePublished="2021-12-24",  # type: ignore
        duration=105,
    )

    # auto generate an id for testing
    payload_dict = payload.model_dump()
    payload_dict["id"] = 1
    movie = Movie(**payload_dict)
    assert movie.yearReleased == 2021

def test_dump():
    movie = Movie(id=1, title="Ponyo", movieGenres=["Animation"], duration=103)
    dumped = movie.model_dump()
    assert dumped["duration"] == 103
    assert dumped["title"] == "Ponyo"
    assert dumped["movieGenres"] == ["Animation"]
