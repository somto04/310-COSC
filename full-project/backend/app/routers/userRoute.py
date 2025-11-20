from typing import List
from fastapi import APIRouter, status, HTTPException, Form, Depends
from app.routers.auth import getCurrentUser
from ..schemas.user import User, UserCreate, UserUpdate
from ..services.userService import listUsers, createUser, deleteUser, updateUser, getUserById

router = APIRouter(prefix = "/users", tags = ["users"])

@router.get("", response_model=List[User])
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
def postUser(payload: UserCreate):
    return createUser(payload)

@router.get("/{userId}", response_model = User)
def getUser(userId: str):
    return getUserById(userId)

@router.put("/{userId}", response_model = User)
def putUser(userId: str, payload: UserUpdate):
    return updateUser(userId, payload)

@router.delete("/{userId}", status_code=status.HTTP_204_NO_CONTENT)
def removeUser(userId: str):
    deleteUser(userId)
    return None

@router.get("/userProfile/{userId}")
def getUserProfile(userId: str, currentUser = Depends(getCurrentUser)):
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
