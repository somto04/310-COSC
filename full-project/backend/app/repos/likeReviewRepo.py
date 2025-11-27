from typing import List
from ..schemas.likeReview import LikeReview
from .repo import _baseLoadAll, _baseSaveAll, DATA_DIR

FILE = DATA_DIR / "likeReviews.json"
def loadLikeReviews() -> List[LikeReview]:
    raw = _baseLoadAll(FILE)
    return [LikeReview(**like) for like in raw]

def saveLikeReviews(likes: List[LikeReview]):
    raw = [like.model_dump() for like in likes]
    _baseSaveAll(FILE, raw)