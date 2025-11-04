
from pydantic import BaseModel, Field, model_validator
from typing import List, Optional

class Movie(BaseModel):
    id: int
    title: str
    movieIMDbRating: float
    movieGenres: List[str]
    directors: List[str] = Field(default_factory=list)
    mainStars: List[str] = Field(default_factory=list)
    description: Optional[str] = None
    datePublished: Optional[str] = None
    duration: int  # minutes
    yearReleased: Optional[int] = None

    @model_validator(mode="before")
    def accept_legacy_keys(cls, values):
        # id aliases
        if "movieId" in values and "id" not in values:
            values["id"] = int(values.pop("movieId"))
        if "id" in values:
            values["id"] = int(values["id"])

        # title alias
        if "movieName" in values and "title" not in values:
            values["title"] = values.pop("movieName")

        # alias for length
        if "length" in values and "duration" not in values:
            values["duration"] = values.pop("length")

        # handle year alias
        if "year" in values and "yearReleased" not in values:
            values["yearReleased"] = int(values.pop("year"))

        # extract year from datePublished if yearReleased not provided
        if "yearReleased" not in values and "datePublished" in values and values["datePublished"]:
            try:
                values["yearReleased"] = int(str(values["datePublished"])[:4])
            except (ValueError, TypeError):
                pass

        return values

class MovieCreate(BaseModel):
    
    title: str
    movieIMDbRating: float
    movieGenres: List[str]
    directors: List[str] = Field(default_factory=list)
    mainStars: List[str] = Field(default_factory=list)
    description: Optional[str] = None
    datePublished: Optional[str] = None  # ISO date string
    duration: int  # minutes
    yearReleased: Optional[int] = None

    @model_validator(mode="before")
    def accept_legacy_create_keys(cls, values):
        if "movieName" in values and "title" not in values:
            values["title"] = values.pop("movieName")
        if "length" in values and "duration" not in values:
            values["duration"] = values.pop("length")
        return values

class MovieUpdate(BaseModel):
    
    title: Optional [str] = None
    movieIMDbRating: Optional[float] = None
    movieGenres: Optional[List[str]] = None
    directors: Optional[List[str]] = Field(default_factory=list)
    mainStars: Optional[List[str]] = Field(default_factory=list)
    description: Optional[str] = None
    datePublished: Optional[str] = None  # ISO date string
    duration: Optional[int] = None # minutes
    yearReleased: Optional[int] = None