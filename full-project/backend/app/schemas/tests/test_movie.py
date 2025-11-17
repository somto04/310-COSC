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


def test_update_movie_imdb_rating():
    update_data = MovieUpdate(movieIMDbRating=8.5)  # type: ignore
    assert update_data.movieIMDbRating == 8.5


def test_update_existing_movie():
    movie = Movie(
        id=1,
        title="Evangelion: 1.0 You Are (Not) Alone",
        movieGenres=["Animation", "Sci-Fi"],
        duration=110,
    )

    update_data = MovieUpdate(title="tee hee change the title", movieIMDbRating=9.0)  # type: ignore
    update_data_dict = update_data.model_dump(exclude_unset=True)
    updated_movie = movie.model_copy(update=update_data_dict)
    assert updated_movie.title == "tee hee change the title"
    assert updated_movie.movieIMDbRating == 9.0
    assert updated_movie.duration == 110  # unchanged
    assert updated_movie.movieGenres == ["Animation", "Sci-Fi"]  # unchanged
    assert updated_movie.id == 1  # unchanged
    assert updated_movie.mainStars == []  # default value
    assert updated_movie.directors == []  # default value
    assert updated_movie.description is None  # default value
    assert updated_movie.datePublished is None  # default value
    assert updated_movie.yearReleased is None  # default value


def test_invalid_imdb_rating():
    with pytest.raises(ValidationError):
        Movie(
            id=2,
            title="Bad Movie",
            movieGenres=["Drama"],
            duration=90,
            movieIMDbRating=15.0,  # Invalid rating # type: ignore
        )
