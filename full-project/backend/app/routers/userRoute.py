from typing import List
from fastapi import APIRouter, status, HTTPException, Form, Depends
from app.routers.auth import getCurrentUser
from ..schemas.user import User, UserCreate, UserUpdate
from ..services.userService import listUsers, createUser, deleteUser, updateUser, getUserById, UserNotFoundError, UsernameTakenError, EmailNotFoundError


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
    try: 
        return createUser(payload)
    except UsernameTakenError:
        raise HTTPException(status_code=409, detail="Username already taken; retry.")

@router.get("/{userId}", response_model = User)
def getUser(userId: int):
    try:
        return getUserById(userId)
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail=f"User '{userId}' not found")

@router.put("/{userId}", response_model = User)
def putUser(userId: int, payload: UserUpdate):
    try:
        return updateUser(userId, payload)
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail=f"User '{userId}' not found")

@router.delete("/{userId}", status_code=status.HTTP_204_NO_CONTENT)
def removeUser(userId: int):
    try:
        deleteUser(userId)
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail=f"User '{userId}' not found")

@router.get("/userProfile/{userId}")
def getUserProfile(userId: int, currentUser = Depends(getCurrentUser)):
    """
    Gets the user profile of either the owner or another reviewer

    Returns:
        User profile.
    
    Raises:
        HTTPException: If the user doesnt exist.
    """
    try:
        user = getUserById(userId)
        isOwner = currentUser.id == userId
        return {"user": user, "isOwner": isOwner}
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail=f"User '{userId}' not found")