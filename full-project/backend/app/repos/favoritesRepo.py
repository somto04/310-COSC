from typing import List
from ..schemas.favorites import Favorite
from .repo import _baseLoadAll, _baseSaveAll, DATA_DIR

FILE = DATA_DIR / "favorites.json"

def loadFavorites() -> List[Favorite]:
    raw = _baseLoadAll(FILE)
    return [Favorite(**fav) for fav in raw]

def saveFavorites(favs: List[Favorite]):
    raw = [f.model_dump() for f in favs]
    _baseSaveAll(FILE, raw)
