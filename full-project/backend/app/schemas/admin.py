from pydantic import BaseModel
from typing import List
from ..schemas.review import Review

class AdminFlagResponse(BaseModel):
    message: str
    userId: int
    penaltyCount: int
    isBanned: bool

class PaginatedFlaggedReviewsResponse(BaseModel):
    page: int
    pageSize: int
    totalFlagged: int
    pageCount: int
    reviews: List[Review]
