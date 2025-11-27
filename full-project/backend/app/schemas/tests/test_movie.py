import pytest
from ..movie import Movie, MovieCreate, MovieUpdate
from datetime import date
from pydantic import ValidationError


def test_movieValidInput():
    movie = Movie(
        id=1,
        tmdbId=123456,
        title="Test",
        movieGenres=["Drama"],
        datePublished="2020-01-01",  # type: ignore
        duration=120,
    )
    assert movie.datePublished.year == 2020  # type: ignore


def test_movieInvalidDate():
    with pytest.raises(ValidationError):
        Movie(
            id=1,
            tmdbId=123456,
            title="Test",
            movieGenres=["Drama"],
            datePublished="invalid-date",  # type: ignore
            duration=120,
        )


def test_movieAliases():
    movie = Movie(
        id=1,
        tmdbId=654321,
        movieGenre=["Action"],  # legacy key # type: ignore
        movieName="Thing",  # type: ignore
        duration=100,
    )
    assert movie.movieGenres == ["Action"]


def test_defaultFactoryLists():
    m1 = MovieCreate(tmdbId=0, title="Bullet Train", movieGenres=["Action"], duration=120)
    m2 = MovieCreate(tmdbId=1, title="Oppenheimer", movieGenres=["Drama"], duration=180)

    assert m1.directors == []
    assert m2.directors == []
    assert m1.directors is not m2.directors  # ensure fresh list each time


def test_extractYearFromDatePipeline():
    payload = MovieCreate(
        tmdbId=789012,
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
    movie = Movie(id=1,tmdbId=2344, title="Ponyo", movieGenres=["Animation"], duration=103)
    dumped = movie.model_dump()
    assert dumped["duration"] == 103
    assert dumped["title"] == "Ponyo"
    assert dumped["movieGenres"] == ["Animation"]


def test_updateMovieImdbRating():
    updateData = MovieUpdate(movieIMDbRating=8.5)  # type: ignore
    assert updateData.movieIMDbRating == 8.5


def test_updateExistingMovie():
    movie = Movie(
        id=1,
        tmdbId=5678,
        title="Evangelion: 1.0 You Are (Not) Alone",
        movieGenres=["Animation", "Sci-Fi"],
        duration=110,
    )

    updateData = MovieUpdate(title="tee hee change the title", movieIMDbRating=9.0)  # type: ignore
    updateDataDict = updateData.model_dump(exclude_unset=True)
    updatedMovie = movie.model_copy(update=updateDataDict)
    assert updatedMovie.title == "tee hee change the title"
    assert updatedMovie.movieIMDbRating == 9.0
    assert updatedMovie.duration == 110  # unchanged
    assert updatedMovie.movieGenres == ["Animation", "Sci-Fi"]  # unchanged
    assert updatedMovie.id == 1  # unchanged
    assert updatedMovie.mainStars == []  # default value
    assert updatedMovie.directors == []  # default value
    assert updatedMovie.description is None  # default value
    assert updatedMovie.datePublished is None  # default value
    assert updatedMovie.yearReleased is None  # default value


def test_invalidImdbRating():
    with pytest.raises(ValidationError):
        Movie(
            id=2,
            tmdbId=999999,
            title="Bad Movie",
            movieGenres=["Drama"],
            duration=90,
            movieIMDbRating=15.0,  # Invalid rating # type: ignore
        )
