from pydantic import BaseModel # automatically checks data types when making a new instance
from typing import List, Optional

class Movie(BaseModel):
    movieId: int
    movieName: str
    yearReleased: int
    actors: Optional[List[str]] = []
    genre: str
    length: int # mins

class MovieCreate(BaseModel):
    movieName: str
    yearReleased: int
    actors: Optional[List[str]] = []
    genre: str
    length: int

class MovieUpdate(BaseModel):
    movieName: Optional[str] = None
    yearReleased: Optional[int] = None
    actors: Optional[List[str]] = None
    genre: Optional[str] = None
    length: Optional[int] = None
