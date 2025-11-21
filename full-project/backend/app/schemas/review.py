from pydantic import BaseModel, Field
from typing import Optional

MIN_REVIEW_TITLE_LENGTH = 5
MAX_REVIEW_TITLE_LENGTH = 100
MIN_REVIEW_BODY_LENGTH = 10
MAX_REVIEW_BODY_LENGTH = 1000
MIN_RATING = 1
MAX_RATING = 10


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
    reviewTitle: str = Field(
        min_length=MIN_REVIEW_TITLE_LENGTH,
        max_length=MAX_REVIEW_TITLE_LENGTH,
        description=f"title of your review, must be between {MIN_REVIEW_TITLE_LENGTH} and {MAX_REVIEW_TITLE_LENGTH} characters",
    )
    reviewBody: str = Field(
        min_length=MIN_REVIEW_BODY_LENGTH,
        max_length=MAX_REVIEW_BODY_LENGTH,
        description=f"body of your review, must be between {MIN_REVIEW_BODY_LENGTH} and {MAX_REVIEW_BODY_LENGTH} characters",
    )
    rating: int = Field(
        ge=MIN_RATING,
        le=MAX_RATING,
        description=f"rating of the movie from {MIN_RATING} to {MAX_RATING}",
    )


class ReviewUpdate(BaseModel):
    reviewTitle: Optional[str] = Field(
        default=None,
        min_length=MIN_REVIEW_TITLE_LENGTH,
        max_length=MAX_REVIEW_TITLE_LENGTH,
        description=f"title of your review, must be between {MIN_REVIEW_TITLE_LENGTH} and {MAX_REVIEW_TITLE_LENGTH} characters",
    )
    reviewBody: Optional[str] = Field(
        default=None,
        min_length=MIN_REVIEW_BODY_LENGTH,
        max_length=MAX_REVIEW_BODY_LENGTH,
        description=f"body of your review, must be between {MIN_REVIEW_BODY_LENGTH} and {MAX_REVIEW_BODY_LENGTH} characters",
    )
    rating: Optional[int] = Field(
        default=None,
        ge=MIN_RATING,
        le=MAX_RATING,
        description=f"rating of the movie from {MIN_RATING} to {MAX_RATING}",
    )
