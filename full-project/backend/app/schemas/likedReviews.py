from pydantic import BaseModel

class LikedReview(BaseModel):
    userId: int
    reviewId: int