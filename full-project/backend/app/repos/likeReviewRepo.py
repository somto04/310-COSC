from typing import List
from ..schemas.likedReviews import LikedReview
from .repo import _baseLoadAll, _baseSaveAll, DATA_DIR

FILE = DATA_DIR / "likeReviews.json"
def loadLikeReviews() -> List[LikedReview]:
    raw = _baseLoadAll(FILE)
    return [LikedReview(**like) for like in raw]

def saveLikeReviews(likes: List[LikedReview]):
    raw = [like.model_dump() for like in likes]
    _baseSaveAll(FILE, raw)