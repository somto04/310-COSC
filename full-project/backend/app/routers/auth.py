from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordBearer
from ..schemas.user import User
from ..repos.userRepo import loadUsers
from app.utilities.security import verifyPassword
from ..schemas.user import CurrentUser
from ..services.userService import get_user_by_email, generateResetToken, resetPassword

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def getUsernameFromJsonDB(username: str) -> User | None:
    users = loadUsers()
    for user in users:
        if user.username == username:
            return user
    return None

def getCurrentUser(token: str = Depends(oauth2_scheme)) -> CurrentUser:
    user = getUsernameFromJsonDB(token)
    validateUser(user)

    userId = user.get("id") or user.get("userId")

    return CurrentUser(
        id=userId,
        username=user["username"],
        role=user["role"]
    )

def requireAdmin(user: CurrentUser = Depends(getCurrentUser)):
    validateUser(user)
    
    if user.role != "admin":
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
def logout(currentUser: CurrentUser = Depends(getCurrentUser)):
    """
        Logs the current user out by clearing or invalidating their token/session.
    """
    return {
        "message": f"User '{currentUser.username}' has been logged out successfully."
    }

@router.get("/adminDashboard")
def getAdminDashboard(admin = Depends(requireAdmin)):
    return {"message": "Welcome to the admin dashboard"}

@router.post("/forgot-password")
def forgotPassword(email: str = Form(...)):
    """
    Simulate sending a password reset link to the user's email.

    Returns:
        Message saying link was sent.

    Raises: 
        HTTPException: invalid email.
    """
    if not get_user_by_email(email):
        raise HTTPException(status_code=404, detail="Email not found")

    token = generateResetToken(email)
    return {"message": "Password reset link sent", "token": token}


@router.post("/reset-password")
def resettingPassword(token: str = Form(...), new_password: str = Form(...)):
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
