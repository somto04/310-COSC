from typing import List
from fastapi import APIRouter, status, HTTPException, Form, Depends
from app.routers.auth import getCurrentUser
from ..schemas.user import User, UserCreate, UserUpdate, SafeUser
from ..services.userService import listUsers, createUser, deleteUser, updateUser, getUserById
from fastapi import Body
from ..schemas.role import Role
from ..repos.movieRepo import loadAll

router = APIRouter(prefix = "/users", tags = ["users"])

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
    return createUser(payload)

@router.get("/{userId}", response_model = SafeUser)
def getUser(userId: int):
    return getUserById(userId)

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
    return updateUser(userId, payload)

@router.delete("/{userId}", status_code=status.HTTP_204_NO_CONTENT)
def removeUser(userId: int, currentUser = Depends(getCurrentUser)):

    if currentUser.role != Role.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized to delete users.")
    
    deleteUser(userId)
    return None

@router.get("/userProfile/{userId}")
def getUserProfile(userId: int, currentUser = Depends(getCurrentUser)):
    """
    Gets the user profile of either the owner or another reviewer

    Returns:
        User profile.
    
    Raises:
        HTTPException: If the user doesnt exist.
    """
    user = getUserById(userId)
    isOwner = currentUser.id == userId
    return {"user": user, "isOwner": isOwner}

@router.get("/{userId}/watchlist")
def getUserWatchlist(userId: int):
    """
    Gets the user's watchlist

    Returns: 
        List of movie ids that the user has added to their watchlist
    """
    user = getUserById(userId)
    movies = loadAll()
    moviesToWatch = [movies[movieId] for movieId in user["watchlist"] if movieId in movies]
    return {"watchlist": moviesToWatch}
