from fastapi import APIRouter, status, Depends, HTTPException, Form
from app.routers.auth import getCurrentUser, getUsernameFromJsonDB
from app.utilities.security import verifyPassword

router = APIRouter()

@router.get("/adminDashboard")
def getAdminDashboard(currentUser = Depends(getCurrentUser)):
    if currentUser.get("role") == "admin":
        return {"message": "Welcome to the admin dashboard"}
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Admin privileges required"
    )

@router.post("/token")
def login(username: str = Form(...), password: str = Form(...)):
    user = getUsernameFromJsonDB(username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Block banned users before verifying password
    if user.get("isBanned"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account banned due to repeated violations",
        )

    hashedPw = user.get("pw")
    if not verifyPassword(password, hashedPw):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "message": "Login successful",
        "accessToken": username,   # temporary token
        "tokenType": "bearer"
    }
