from pydantic import BaseModel, Field, model_validator, Field, AliasChoices
from typing import List, Optional
from decimal import Decimal
from datetime import date

EARLIEST_FILM_YEAR = 1888  # first known motion picture release year
LATEST_REASONABLE_YEAR = 2100
IMDB_MIN = 1.0  # IMDb never goes below 1.0
IMDB_MAX = 10.0  # IMDb max rating
IMDB_MAX_DIGITS = 3  # e.g., "10.0" has 3 digits
IMDB_DECIMALS = 1  # One decimal place like IMDb uses


class Movie(BaseModel):
    """
    Represents a movie in the database with various attributes, such as title, genres, release date, and ratings.

    Handles legacy field names using validation aliases and extracts the release year from the publication date if not explicitly provided.
    """

    id: int = Field(validation_alias=AliasChoices("id", "movieId"))
    title: str = Field(validation_alias=AliasChoices("title", "movieName"))
    movieIMDbRating: Optional[Decimal] = Field(
        default=None,
        ge=IMDB_MIN,
        le=IMDB_MAX,
        max_digits=IMDB_MAX_DIGITS,
        decimal_places=IMDB_DECIMALS,
        validation_alias=AliasChoices("movieIMDb", "movieIMDbRating"),
    )
    movieGenres: List[str] = Field(
        validation_alias=AliasChoices("movieGenre", "movieGenres")
    )
    directors: List[str] = Field(default_factory=list)
    mainStars: List[str] = Field(
        default_factory=list, validation_alias=AliasChoices("mainstars", "mainStars")
    )
    description: Optional[str] = None
    datePublished: Optional[date] = None
    duration: int = Field(
        gt=0, validation_alias=AliasChoices("duration", "length")
    )  # minutes
    yearReleased: Optional[int] = Field(
        default=None,
        ge=EARLIEST_FILM_YEAR,
        le=LATEST_REASONABLE_YEAR,
        validation_alias=AliasChoices("yearReleased", "year"),
    )

    @model_validator(mode="before")
    @classmethod
    def extractYear(cls, values):
        pubDate = values.get("datePublished")
        year = values.get("yearReleased")

        # extract year from datePublished if yearReleased not provided
        if year is None and isinstance(pubDate, date):
            values["yearReleased"] = pubDate.year

        return values


class MovieCreate(BaseModel):
    """
    Request schema for creating a new movie entry.

    Only description, datePublished, and yearReleased are optional.
    """

    title: str = Field(validation_alias=AliasChoices("title", "movieName"))
    movieGenres: List[str] = Field(
        validation_alias=AliasChoices("movieGenre", "movieGenres")
    )
    directors: List[str] = Field(default_factory=list)
    mainStars: List[str] = Field(
        default_factory=list, validation_alias=AliasChoices("mainstars", "mainStars")
    )
    description: Optional[str] = None
    datePublished: Optional[date] = None  # ISO date string
    duration: int = Field(
        gt=0, validation_alias=AliasChoices("duration", "length")
    )  # minutes
    yearReleased: Optional[int] = Field(
        default=None,
        ge=EARLIEST_FILM_YEAR,
        le=LATEST_REASONABLE_YEAR,
        validation_alias=AliasChoices("yearReleased", "year"),
    )


class MovieUpdate(BaseModel):
    """
    Request schema for updating an existing movie entry.

    All fields are optional to allow partial updates.
    """

    title: Optional[str] = Field(
        default=None, validation_alias=AliasChoices("title", "movieName")
    )
    movieIMDbRating: Optional[Decimal] = Field(
        default=None,
        ge=IMDB_MIN,
        le=IMDB_MAX,
        max_digits=IMDB_MAX_DIGITS,
        decimal_places=IMDB_DECIMALS,
        validation_alias=AliasChoices("movieIMDb", "movieIMDbRating"),
    )
    movieGenres: Optional[List[str]] = Field(
        default=None, validation_alias=AliasChoices("movieGenre", "movieGenres")
    )
    directors: Optional[List[str]] = None
    mainStars: Optional[List[str]] = Field(
        default=None, validation_alias=AliasChoices("mainstars", "mainStars")
    )
    description: Optional[str] = None
    datePublished: Optional[date] = None  # ISO date string
    duration: Optional[int] = Field(
        default=None, gt=0, validation_alias=AliasChoices("duration", "length")
    )  # minutes
    yearReleased: Optional[int] = Field(
        default=None,
        ge=EARLIEST_FILM_YEAR,
        le=LATEST_REASONABLE_YEAR,
        validation_alias=AliasChoices("yearReleased", "year"),
    )
