from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordBearer
import json

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def getUserFromJson(username: str):
    with open("app/data/users.json", "r") as f:
        users = json.load(f)
    for user in users:
        if user["username"] == username:
            return user
    return None

# currently just the username not an actual token
def decodeToken(token: str):
    user = getUserFromJson(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

def getCurrentUser(token: str = Depends(oauth2_scheme)):
    return decodeToken(token)

# checks if the current user is an admin
def requireAdmin(user: dict = Depends(getCurrentUser)):
    if user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return user

# logging in returns a token which is currently just the username
@router.post("/token")
def login(username: str = Form(...), password: str = Form(...)):
    user = getUserFromJson(username)
    if not user or user.get("pw") != password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": username, "token_type": "bearer"}
