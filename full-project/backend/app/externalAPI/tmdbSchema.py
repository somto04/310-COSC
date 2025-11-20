from pydantic import BaseModel
from typing import Optional

class TMDbMovie(BaseModel):
    id: int
    title: str
    poster: Optional[str]
    overview: Optional[str]
    rating: Optional[float]


class TMDbRecommendation(BaseModel):
    id: int
    title: str
    poster: Optional[str]
    rating: Optional[float]
