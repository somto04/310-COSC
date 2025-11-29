from typing import List
from fastapi import APIRouter, status, HTTPException, Form, Depends
from app.routers.authRoute import getCurrentUser
from ..schemas.user import User, UserCreate, UserUpdate, SafeUser
from ..services.userService import listUsers, createUser, deleteUser, updateUser, getUserById, UserNotFoundError, UsernameTakenError, EmailTakenError
from fastapi import Body
from ..schemas.role import Role
from ..repos.movieRepo import loadMovies
from ..repos.userRepo import loadUsers
from ..services.favoritesService import MovieNotFoundError
import logging
import sys

router = APIRouter(prefix = "/users", tags = ["users"])

class notOwnerError(Exception):
    pass

@router.get("", response_model=List[SafeUser])
def getUsers(page: int = 1, limit: int = 25):
    if page < 1:
        page = 1
    if limit < 1:
        limit = 25

    users = listUsers()   # returns full list of User models

    start = (page - 1) * limit
    end = start + limit

    return users[start:end]


@router.post("", response_model=User, status_code=201)
def createNewUser(payload: UserCreate = Body(
      example={
        "username": "username123",
        "firstName": "user",
        "lastName": "name",
        "age": 20,
        "email": "user@example.com",
        "pw": "MyPassword123!"
      }
)):
    try:
        return createUser(payload)
    except UsernameTakenError as e:
        raise HTTPException(status_code=409, detail=str(e))

@router.get("/watchlist")
def getUserWatchlist(currentUser = Depends(getCurrentUser)):
    """
    Gets the user's watchlist
    """
    user = getUserById(currentUser.id)
    movies = {movie.id: movie for movie in loadMovies()}  # dict keyed by ID
    watchlistIds = getWatchlist(user)

    moviesToWatch = [movies[movieId] for movieId in watchlistIds if movieId in movies]
    return {"watchlist": moviesToWatch}

@router.get("/{userId}", response_model = SafeUser)
def getUser(userId: int):
    try:
        return getUserById(userId)
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.put("/{userId}", response_model = User)
def updatedUser(userId: int, payload: UserUpdate= Body(
      example={
        "username": "username123",
        "firstName": "user",
        "lastName": "name",
        "age": 20,
        "email": "user@example.com",
        "pw": "MyPassword123!"
      }), currentUser = Depends(getCurrentUser)):
     # Only the owner can update their own info
    if currentUser.id != userId:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to update this account."
        )
    try:
        return updateUser(userId, payload)
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except UsernameTakenError as e:
        raise HTTPException(status_code=409, detail=str(e))

@router.delete("/{userId}", status_code=status.HTTP_204_NO_CONTENT)
def removeUser(userId: int, currentUser = Depends(getCurrentUser)):

    if currentUser.role != Role.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized to delete users.")
    try:
        deleteUser(userId)
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    return None

@router.get("/userProfile")
def getUserProfile(userId: int, currentUser = Depends(getCurrentUser)):
    """
    Gets the user profile of either the owner or another reviewer

    Returns:
        User profile.
    
    Raises:
        Exception: If the user doesnt exist.
    """
    try:
        user = getUserById(userId)
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    else:       
        isOwner = currentUser.id == userId
        return {"user": user, "isOwner": isOwner}
    

@router.post("/watchlist/{movieId}")
def addMovieToWatchlist(movieId: int, currentUser = Depends(getCurrentUser)):
    """
    Adds a movie to the user's watchlist
    """
    movies = {movie.id: movie for movie in loadMovies()}
    user = getUserById(currentUser.id)
    watchlist = getWatchlist(user)

    if movieId not in movies:
        raise MovieNotFoundError("This movie does not exist")
    
    if movieId in watchlist:
        return {"watchlist": watchlist}

    updatedWatchlist = watchlist + [movieId]
    updatedUser = updateUser(currentUser.id, UserUpdate(watchlist=updatedWatchlist))

    # Debug prints
    logging.debug(">>> Updated watchlist in memory:", updatedUser.watchlist, file=sys.stderr)
    all_users = loadUsers()
    for u in all_users:
        if u.id == currentUser.id:
            logging.debug(">>> Watchlist from storage:", u.watchlist, file=sys.stderr)

    return {"watchlist": updatedWatchlist}

@router.delete("/watchlist/{movieId}")
def removeMovieFromWatchlist(movieId: int, currentUser = Depends(getCurrentUser)):
    """
    Adds a movie to the users watchlist
    """
    movies = {movie.id: movie for movie in loadMovies()}
    user = getUserById(currentUser.id)
    watchlist = getWatchlist(user)

    if movieId not in movies:
        raise MovieNotFoundError("This movie does not exist")
    
    if movieId not in watchlist:
        return {"message": "Movie not in watchlist"}

    updatedWatchlist = [movie for movie in watchlist if movie != movieId]
    updateUser(currentUser.id, UserUpdate(watchlist=updatedWatchlist))
    return {"message": "movie removed", "watchlist": updatedWatchlist}

def getWatchlist(user):
    return user.watchlist if hasattr(user, "watchlist") else user["watchlist"]
