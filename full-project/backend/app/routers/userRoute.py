from typing import List
from fastapi import APIRouter, status
from ..schemas.user import User, UserCreate, UserUpdate
from ..services.userService import listUsers, createUser, deleteUser, updateUser, getUserById

router = APIRouter(prefix = "/users", tags = ["users"])

@router.get("", response_model=List[User])
def getUsers():
    return listUsers()

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