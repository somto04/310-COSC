
from pydantic import BaseModel

class Favorite(BaseModel):
    userId: int
    movieId: int
