from pydantic import BaseModel
from typing import Optional

class Review(BaseModel):
    id: str
    movieId: int
    userId: int
    reviewTitle: str
    reviewBody: str
    rating: str
    datePosted: Optional[str] = None

class ReviewCreate(BaseModel):
    movieId: int
    userId: int
    reviewTitle: str
    reviewBody: str
    rating: str
    datePosted: Optional[str] = None
    flagged: Optional[bool] = False

class ReviewUpdate(BaseModel):
    movieId: Optional[int] = None
    userId: Optional[int] = None
    reviewTitle: Optional[str] = None
    reviewBody: Optional[str] = None
    rating: Optional[str] = None
    datePosted: Optional[str] = None
    flagged: Optional[bool] = None
