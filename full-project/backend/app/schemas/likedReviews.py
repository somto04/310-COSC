from pydantic import BaseModel
from typing import Optional

class LikedReview(BaseModel):
    userId: int
    reviewId: int

class LikedReviewFull(BaseModel):
    id: int
    movieId: int
    movieTitle: str
    username: str
    reviewTitle: str
    poster: Optional[str] = None 