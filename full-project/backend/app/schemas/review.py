from pydantic import BaseModel
from typing import Optional
from decimal import Decimal

class Review(BaseModel):
    id: int
    movieId: int
    userId: int
    reviewTitle: str
    reviewBody: str
    rating: Decimal
    datePosted: Optional[str] = None
    flagged: Optional[bool] = False

class ReviewCreate(BaseModel):
    movieId: int
    userId: Optional[int] = None 
    reviewTitle: str
    reviewBody: str
    rating: Decimal
    datePosted: Optional[str] = None
    flagged: Optional[bool] = False

class ReviewUpdate(BaseModel):
    movieId: Optional[int] = None
    userId: Optional[int] = None
    reviewTitle: Optional[str] = None
    reviewBody: Optional[str] = None
    rating: Optional[Decimal] = None
    datePosted: Optional[str] = None
    flagged: Optional[bool] = None

class Reply(BaseModel):
    id: int
    reviewId: int
    userId: int
    replyBody: str
    datePosted: str

class ReplyCreate(BaseModel):
    reviewId: int
    userId: int
    replyBody: str
    datePosted: str
