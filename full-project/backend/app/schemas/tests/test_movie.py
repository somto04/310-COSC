import pytest
from ..movie import Movie
from datetime import date

def test_movie_valid_input():
    movie = Movie(
        id=1,
        title="Test",
        movieGenres=["Drama"],
        datePublished="2020-01-01", # type: ignore
        duration=120
    )
    assert movie.datePublished.year == 2020 # type: ignore
