from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordBearer
from ..repos.userRepo import loadAll, saveAll
#from ..utilities.security import verifyPassword

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
    Login endpoint that validates username and password and returns a token.
    The token is simply the username in this implementation.
    """
    user = getUsernameFromJsonDB(username)
    result = validateUsernameAndPw(username, password, user)
    return result

@router.get("/adminDashboard")
def getAdminDashboard(admin = Depends(requireAdmin)):
    return {"message": "Welcome to the admin dashboard"}

def validateUsernameAndPw(username, password, user):
    user = getUsernameFromJsonDB(username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # hashed pw not yet implemented on this branch
    #hashedPw = user.get("pw")
    if user.get("pw") != password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {"access_token": username, "token_type": "bearer", "role": user.get("role"),}

def validateUser(user):
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
