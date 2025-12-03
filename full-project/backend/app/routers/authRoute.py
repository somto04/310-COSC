from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import datetime, timedelta
from ..schemas.user import CurrentUser, Password, Email, Username
from ..schemas.role import Role
from fastapi.responses import RedirectResponse
from ..services.userService import getUserByEmail, getUserByUsername
from ..services.authService import (
    validatePassword,
    ensureUserExists,
    generateResetToken,
    resetPassword,
    UserNotFoundError,
    InvalidPasswordError,
)

SECRET_KEY = "CHANGEME"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# ==================================HELPER FUNCTIONS==================================

def createAccessToken(username: str):
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    toEncode = {"sub": username, "exp": expire}
    return jwt.encode(toEncode, SECRET_KEY, algorithm=ALGORITHM)

def decodeAccesstoken(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None

def getCurrentUser(token: str = Depends(oauth2_scheme)) -> CurrentUser:
    """
    Resolve the current user from the bearer token (username for now).
    Maps domain errors to HTTP errors.
    """
    username = decodeAccesstoken(token)
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        user = ensureUserExists(getUserByUsername(username))
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return CurrentUser(id=user.id, username=user.username, role=user.role)


def requireAdmin(currentUser: CurrentUser = Depends(getCurrentUser)) -> CurrentUser:
    if currentUser.role != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return currentUser


# =================================ROUTE HANDLERS==================================


@router.post("/token")
def login(
   username: Annotated[
        Username,
        Form(
            ...,
            examples=["testuser"]
        )
    ],
    password: Annotated[
        Password,
        Form(
            ...,
            examples=["Password123!"]
        )
    ],
):
    """
    Logs in user and blocks banned users before their password is validated.
    All domain auth errors are mapped to HTTP here.
    """
    try:
        user = ensureUserExists(getUserByUsername(username))

        if user.isBanned:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account banned due to repeated violations",
            )

        validatePassword(user, password)

    except (UserNotFoundError, InvalidPasswordError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "message": "Login successful",
        "access_token": createAccessToken(username),
        "token_type": "bearer",
        "userId": user.id,
    }


@router.post("/logout")
def logout(currentUser: CurrentUser = Depends(getCurrentUser)):
    """
    Logs the current user out by clearing or invalidating their token/session.
    """
    return {
        "message": f"User '{currentUser.username}' has been logged out successfully."
    }


@router.get("/adminDashboard")
def getAdminDashboard(admin: CurrentUser = Depends(requireAdmin)):
    return {"message": "Welcome to the admin dashboard"}


@router.post("/forgot-password")
def forgotPassword(email: Annotated[Email, Form(...)]):
    """
    Simulate sending a password reset link to the user's email.

    Raises:
        HTTPException: if the email is not associated with a user.
    """
    try:
        ensureUserExists(getUserByEmail(email))
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="Email not found")

    token = generateResetToken(email)
    return RedirectResponse(
        url=f"/reset-password?token={token}",
        status_code=303
    )

@router.post("/reset-password")
def resettingPassword(
    token: Annotated[str, Form(...)], new_password: Annotated[Password, Form(...)]
):
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
