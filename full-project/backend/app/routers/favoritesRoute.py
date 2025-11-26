from fastapi import APIRouter, Depends, HTTPException
from ..services.favoritesService import addFavorite, removeFavorite, listFavorites, MovieNotFoundError, FavoriteAlreadyExistsError, FavoriteNotFoundError 
from ..schemas.user import CurrentUser
from ..routers.authRoute import getCurrentUser


router = APIRouter(prefix="/favorites", tags=["Favorites"])

@router.get("/")
def getAllFavoriteMovies(currentUser: CurrentUser = Depends(getCurrentUser)):
    return listFavorites(currentUser.id)

@router.post("/{movieId}")
def addFavoriteMovies(movieId: int, currentUser: CurrentUser = Depends(getCurrentUser)):
    try:
        return addFavorite(currentUser.id, movieId)
    except MovieNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))
    except FavoriteAlreadyExistsError as error:
        raise HTTPException(status_code=409, detail=str(error))

@router.delete("/{movieId}")
def removeFavoriteMovie(movieId: int, currentUser: CurrentUser = Depends(getCurrentUser)):
    try:
        return removeFavorite(currentUser.id, movieId)
    except FavoriteNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))

