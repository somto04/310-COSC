from pydantic import BaseModel
from typing import Optional

class Review(BaseModel):
    reviewId: int
    movieId: int
    reveiwTitle: str
    rating: int
    reviewBody: str
    flagged: bool

class ReviewCreate(BaseModel):
    movieId: int
    reveiwTitle: str
    rating: int
    reviewBody: str
    flagged: bool

class reviewUpdate(BaseModel):
    reveiwTitle: Optional[str] = None
    rating: Optional[int] = None
    reviewBody: Optional[str] = None
    flagged: Optional[bool] = None
