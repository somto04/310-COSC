from typing import List
from fastapi import APIRouter, status, HTTPException, Form  
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
def getUserProfile():
    """
    Gets the user profile of either the owner or another reviewer

    Returns:
        Iser profile.
    
    Raises:
        HTTPException: If the user doesnt exist.
    """

@router.post("/forgot-password")
def forgotPassword(email: str = Form(...)):
    """
    Simulate sending a password reset link to the user's email.
    In real projects, this would email a token.
    """
    if not emailExists(email):
        raise HTTPException(status_code=404, detail="Email not found")

    # for now, just return a fake reset token
    token = generateResetToken(email)
    return {"message": "Password reset link sent", "token": token}


@router.post("/reset-password")
def resettingPassword(token: str = Form(...), new_password: str = Form(...)):
    """
    Reset a user's password using the provided token.
    """
    success = resetPassword(token, new_password)
    if not success:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    return {"message": "Password reset successful"}