from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordBearer

from ..schemas.user import CurrentUser, Password, Email, Username
from ..schemas.role import Role
from ..services.userService import getUserByEmail, getUserByUsername
from ..services.authService import (
    validatePassword,
    ensureUserExists,
    generateResetToken,
    resetPassword,
    UserNotFoundError,
    InvalidPasswordError,
)


router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# ==================================HELPER FUNCTIONS==================================


def getCurrentUser(token: str = Depends(oauth2_scheme)) -> CurrentUser:
    """
    Resolve the current user from the bearer token (username for now).
    Maps domain errors to HTTP errors.
    """
    try:
        user = ensureUserExists(getUserByUsername(token))
    except UserNotFoundError:
        # Token is invalid / user no longer exists
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
    username: Annotated[Username, Form(...)],
    password: Annotated[Password, Form(...)],
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
        "access_token": username,  # should be token when implemented
        "token_type": "bearer",
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
    return {"message": "Password reset link sent", "token": token}


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
