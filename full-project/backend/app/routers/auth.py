from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordBearer
import json

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# gets the username from the database
def getUserFromJson(username: str):
    with open("app/data/users.json", "r") as f:
        users = json.load(f)
    for user in users:
        if user["username"] == username:
            return user
    return None

# uses the token  passed through to get the user
def decodeToken(token: str):
    user = getUserFromJson(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

# function used by other files to get the current user - passes in the token
def getCurrentUser(token: str = Depends(oauth2_scheme)):
    return decodeToken(token)

# checks if the current user is an admin
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
    user = getUserFromJson(username)
    # if the username is not found or the password is incorrect
    if not user or user.get("pw") != password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": username, "token_type": "bearer", "role": user.get("role")}

# this is for when an admin is trying to access the admin dashboard via the button
@router.get("/adminDashboard")
# uses the requireAdmin function to verify that they are an admin
def getAdminDashboard(admin = Depends(requireAdmin)):
    return "in admin"

