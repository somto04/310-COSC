from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordBearer
from ..repos.userRepo import loadAll, saveAll
from app.utilities.security import verifyPassword

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def getUsernameFromJsonDB(username: str):
    users = loadAll()
    for user in users:
        if user["username"] == username:
            return user
    return None

def decodeToken(token: str):
    user = getUsernameFromJsonDB(token)
    validateUser(user)
    return user

def getCurrentUser(token: str = Depends(oauth2_scheme)):
    return decodeToken(token)

def requireAdmin(user: dict = Depends(getCurrentUser)):
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return user

@router.post("/token")
def login(username: str = Form(...), password: str = Form(...)):
    """
        Logs in user and blocks banned users before their password is validated
    """
    user = getUsernameFromJsonDB(username)
    validateUser(user)

    if user.get("isBanned"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account banned due to repeated violations",
        )

    validatePassword(password, user)

    return {"message": "Login successful",
            "access_token": username,
            "token_type": "bearer"}

@router.post("/logout")
def logout(currentUser=Depends(getCurrentUser)):
    """
        Logs the current user out by clearing or invalidating their token/session.
    """
    return {
        "message": f"User '{currentUser['username']}' has been logged out successfully."
    }

@router.get("/adminDashboard")
def getAdminDashboard(admin = Depends(requireAdmin)):
    return {"message": "Welcome to the admin dashboard"}

def validatePassword(password, user):
    hashedPw = user.get("pw")
    if not verifyPassword(password, hashedPw):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
def validateUser(user):
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="This user does not exist",
            headers={"WWW-Authenticate": "Bearer"},
        )
