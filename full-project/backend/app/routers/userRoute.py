from typing import List
from fastapi import APIRouter, status, HTTPException, Form, Depends
from app.routers.auth import getCurrentUser
from ..schemas.user import User, UserCreate, UserUpdate, SafeUser
from ..services.userService import listUsers, createUser, deleteUser, updateUser, getUserById, UserNotFoundError, UsernameTakenError, EmailTakenError
from fastapi import Body
from ..schemas.role import Role

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
    try:
        return createUser(payload)
    except UsernameTakenError as e:
        raise HTTPException(status_code=409, detail=str(e))

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

@router.get("/userProfile/{userId}")
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
