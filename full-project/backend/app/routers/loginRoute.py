from fastapi import APIRouter, status, Depends, HTTPException, Form
from auth.py import getCurrentUser

router = APIRouter()

@router.get("/adminDashboard")
def getAdminDashboard(currentUser = Depends(getCurrentUser)):
    if currentUser["role"] == "admin":
        return "in admin "
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )

@router.get("/login")   
def login(username: str = Form(...), password: str = Form(...)):
    user = getCurrentUser(username)
    # if the username is not found or the password is incorrect
    if not user or user.get("pw") != password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )