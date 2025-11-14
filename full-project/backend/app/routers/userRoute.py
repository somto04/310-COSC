from typing import List
from fastapi import APIRouter, status, HTTPException, Form, Depends
from app.routers.auth import getCurrentUser
from ..schemas.user import User, UserCreate, UserUpdate
from ..services.userService import listUsers, createUser, deleteUser, updateUser, getUserById, emailExists, generateResetToken, resetPassword

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

@router.post("/forgot-password")
def forgotPassword(email: str = Form(...)):
    """
    Simulate sending a password reset link to the user's email.

    Returns:
        Message saying link was sent.

    Raises: 
        HTTPException: invalid email.
    """
    if not emailExists(email):
        raise HTTPException(status_code=404, detail="Email not found")

    token = generateResetToken(email)
    return {"message": "Password reset link sent", "token": token}


@router.post("/reset-password")
def resettingPassword(token: str = Form(...), new_password: str = Form(...)):
    """
    Reset a user's password using the provided token.

    Returns:
        Message saying reset was successful.

    Raises: 
        HTTPException: invalid token.
    """
    success = resetPassword(token, new_password)
    if not success:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    return {"message": "Password reset successful"}