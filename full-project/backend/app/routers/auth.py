from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordBearer
from ..schemas.user import User
from ..repos.userRepo import loadUsers
from app.utilities.security import verifyPassword
from ..schemas.user import CurrentUser, Password, Email, Username
from ..schemas.role import Role
from ..services.userService import (
    getUserByEmail,
    generateResetToken,
    resetPassword,
    getUserByUsername,
)


router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# ==================================HELPER FUNCTIONS==================================


def getCurrentUser(token: str = Depends(oauth2_scheme)) -> CurrentUser:
    user = ensureUserExists(getUserByUsername(token))
    return CurrentUser(id=user.id, username=user.username, role=user.role)


def requireAdmin(currentUser: CurrentUser = Depends(getCurrentUser)) -> CurrentUser:
    if currentUser.role != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return currentUser


def validatePassword(password: Password, user: User) -> None:
    if not verifyPassword(password, user.pw):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )


def ensureUserExists(user: User | None) -> User:
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="This user does not exist",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


# =================================ROUTE HANDLERS==================================


@router.post("/token")
def login(username: Username = Form(...), password: Password = Form(...)):
    """
    Logs in user and blocks banned users before their password is validated
    """
    user = ensureUserExists(getUserByUsername(username))

    if user.isBanned:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account banned due to repeated violations",
        )

    validatePassword(password, user)

    return {
        "message": "Login successful",
        "access_token": username,
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
def forgotPassword(email: Email = Form(...)):
    """
    Simulate sending a password reset link to the user's email.

    Returns:
        Message saying link was sent.

    Raises:
        HTTPException: invalid email.
    """
    if not getUserByEmail(email):
        raise HTTPException(status_code=404, detail="Email not found")

    token = generateResetToken(email)
    return {"message": "Password reset link sent", "token": token}


@router.post("/reset-password")
def resettingPassword(token: str = Form(...), new_password: Password = Form(...)):
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
