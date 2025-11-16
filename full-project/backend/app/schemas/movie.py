from pydantic import BaseModel, Field, model_validator, Field, AliasChoices
from typing import List, Optional
from decimal import Decimal
from datetime import date

class Movie(BaseModel):
    id: int = Field(validation_alias = AliasChoices("id", "movieId"))
    title: str = Field(validation_alias = AliasChoices("title", "movieName"))
    movieIMDbRating: Decimal = Field(
        ge = 1.0, 
        le = 10.0,
        max_digits = 3,
        decimal_places = 1)
    movieGenres: List[str]
    directors: List[str] = Field(default_factory = list)
    mainStars: List[str] = Field(default_factory = list)
    description: Optional[str] = None
    datePublished: Optional[date] = None
    duration: int = Field(
        gt = 0,
        validation_alias = AliasChoices("duration", "length"))  # minutes
    yearReleased: Optional[int] = Field(
        default = None,
        ge = 1888,  # The year the first film was made
        le = 2100,
        validation_alias = AliasChoices("yearReleased", "year")
    )

    @model_validator(mode = "before")
    @classmethod
    def extract_year(cls, values):
        pub_date = values.get("datePublished")

        # extract year from datePublished if yearReleased not provided
        if "yearReleased" not in values and isinstance(pub_date, date):
            values["yearReleased"] = pub_date.year

        return values

class MovieCreate(BaseModel):
    title: str = Field(validation_alias = AliasChoices("title", "movieName"))
    movieIMDbRating: float
    movieGenres: List[str]
    directors: List[str] = Field(default_factory = list)
    mainStars: List[str] = Field(default_factory = list)
    description: Optional[str] = None
    datePublished: Optional[str] = None  # ISO date string
    duration: int = Field(validation_alias = AliasChoices("duration", "length")) # minutes
    yearReleased: Optional[int] = None

class MovieUpdate(BaseModel):
    title: Optional[str] = Field(default = None, validation_alias = AliasChoices("title", "movieName"))
    movieIMDbRating: Optional[float] = None
    movieGenres: Optional[List[str]] = None
    directors: Optional[List[str]] = Field(default_factory = list)
    mainStars: Optional[List[str]] = Field(default_factory = list)
    description: Optional[str] = None
    datePublished: Optional[str] = None  # ISO date string
    duration: Optional[int] = Field(default = None, validation_alias = AliasChoices("duration", "length"))  # minutes
    yearReleased: Optional[int] = None