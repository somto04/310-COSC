from fastapi import APIRouter, Depends
from ..services.favoritesService import addFavorite, removeFavorite, listFavorites
from ..schemas.user import CurrentUser
from ..routers.auth import getCurrentUser

router = APIRouter(prefix="/favorites", tags=["Favorites"])

@router.get("/")
def getAllFavoriteMovies(currentUser: CurrentUser = Depends(getCurrentUser)):
    return listFavorites(currentUser.id)

@router.post("/{movieId}")
def addFavoriteMovies(movieId: int, currentUser: CurrentUser = Depends(getCurrentUser)):
    return addFavorite(currentUser.id, movieId)

@router.delete("/{movieId}")
def removeFavoriteMovie(movieId: int, currentUser: CurrentUser = Depends(getCurrentUser)):
    return removeFavorite(currentUser.id, movieId)

