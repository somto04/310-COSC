from pydantic import BaseModel, Field
from typing import Optional

class Review(BaseModel):
    id: int
    movieId: int
    userId: int
    reviewTitle: str
    reviewBody: str
    rating: int = Field(ge=1, le=10)
    datePosted: Optional[str] = None
    flagged: Optional[bool] = False

class ReviewCreate(BaseModel):
    reviewTitle: str #= Field(minLength=3, maxLength=50, description=f"title of your review, must be less than {maxlength} characters")
    reviewBody: str
    rating: int = Field(ge=1, le=10)    

class ReviewUpdate(BaseModel):
    reviewTitle: Optional[str] = None
    reviewBody: Optional[str] = None
    rating: Optional[int] = Field(default=None, ge=1, le=10)    