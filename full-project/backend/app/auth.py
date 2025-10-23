from fastapi import Depends, HTTPException, status, Form, APIRouter
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
import json

router = APIRouter()
oauth2Scheme = OAuth2PasswordBearer(tokenUrl = "token")

# currently only using a username - needs to be swtiched with jwt token once implemented
def getUserFromJson(username: str):
    with open("app/data/users.json", "r") as f:
        users = json.load(f)
    for user in users:
        if user["username"] == username:
            return user
    return None

# needs to be switched with jwt token when implemented
def decodeToken(token: str):
    user = getUserFromJson(token)
    if not user:
        raise HTTPException(status_code = 401, detail = "invalid authentication credentials")
    return user

def getCurrentUser(token: str = Depends(oauth2Scheme)):
    return decodeToken(token)

# token endpoint
@router.post("/token")
def login(username: str = Form(...), password: str = Form(...)):
    # currently token is username
    user = getUserFromJson(username)
    if not user or user.get("pw") != password:
        raise HTTPException(status_code=401, detail = "invalid credentials")
    return {"access_token": username, "token_type": "bearer"}