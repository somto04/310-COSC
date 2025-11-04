from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordBearer
import json

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def getUsernameFromJsonDB(username: str):
    with open("app/data/users.json", "r") as f:
        users = json.load(f)
    for user in users:
        if user["username"] == username:
            return user
    return None

def decodeToken(token: str):
    user = getUsernameFromJsonDB(token)
    validateUser(user)
    return user

# function used by other files to get the current user - passes in the token
def getCurrentUser(token: str = Depends(oauth2_scheme)):
    return decodeToken(token)

# Depends(getCurrentUser) makes sure that the function returns true
def requireAdmin(user: dict = Depends(getCurrentUser)):
    if user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return user

# logging in returns a token which is currently just the username
@router.post("/token")
def login(username: str = Form(...), password: str = Form(...), user: dict = Depends(getCurrentUser)):
    user = getUsernameFromJsonDB(username)
    validateUsernameAndPw(username, password, user)

@router.get("/adminDashboard")
def getAdminDashboard(admin = Depends(requireAdmin)):
    return "in admin"

def validateUsernameAndPw(username, password, user):
    if not user or user.get("pw") != password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": username, "token_type": "bearer", "role": user.get("role")}

def validateUser(user):
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )