import secrets, time
from typing import List
from fastapi import HTTPException
from ..schemas.user import User, UserCreate, UserUpdate
from ..schemas.role import Role
from ..repos.userRepo import getNextUserId, loadUsers, saveUsers
from ..utilities.security import hashPassword, verifyPassword

resetTokens = {}  # token -> {"email": str, "expires": int}


def isUsernameTaken(
    users: List[User], username: str, *, exclude_user_id: int | None = None
) -> bool:
    """
    Check if a username already exists in the user list, case-insensitive.
    Assumes `username` is already Pydantic-validated and stripped.
    Optionally excludes a user ID from the check (useful when updating a user).

    Args:
        users (List[User]): List of existing users.
        username (str): Username to check.
        exclude_user_id (int | None): User ID to exclude from the check (default: None).
    Example:
        "Ichigo76" and "ichigo76" are considered the same.
    """
    normalizedNewUsername = username.lower()

    for user in users:
        if exclude_user_id is not None and user.id == exclude_user_id:
            continue

        normalizedExistingUsername = user.username.lower()
        if normalizedExistingUsername == normalizedNewUsername:
            return True

    return False


def listUsers() -> List[User]:
    """Return all users as User objects"""
    return loadUsers()


def createUser(payload: UserCreate) -> User:
    """
    Create a new user with a unique ID and username and hashed password.

    Args:
        payload (UserCreate): user creation data is already validated, such as username abiding by constraints

    Returns:
        New user (User)

    Raises:
        HTTPException: username already taken

    Expects:
        payload (UserCreate): user creation data is already validated, such as username abiding by constraints
    """
    users = loadUsers()

    if isUsernameTaken(users, payload.username):
        raise HTTPException(status_code=409, detail="Username already taken; retry.")

    hashedPw = hashPassword(payload.pw)

    newUser = User(
        id=getNextUserId(),
        username=payload.username,
        firstName=payload.firstName,
        lastName=payload.lastName,
        age=payload.age,
        email=payload.email,
        pw=hashedPw,
    )

    users.append(newUser)
    saveUsers(users)
    return newUser


def getUserById(userId: int) -> User:
    """
    Get a user by ID

    Args:
        userId (int): ID of the user to retrieve

    Returns:
        User

    Raises:
        HTTPException: user not found
    """
    users = loadUsers()
    for user in users:
        if user.id == userId:
            return user
    raise HTTPException(status_code=404, detail=f"User '{userId}' not found")


def updateUser(userId: int, payload: UserUpdate) -> User:
    """
    Update user info by ID

    Hash password if being updated. Also ensures username uniqueness.
    Args:
        userId (int): ID of the user to update
        payload (UserUpdate): update data is already validated

    Returns:
        Updated user

    Raises:
        HTTPException: user not found
    """
    users = loadUsers()
    updateData = payload.model_dump(exclude_unset=True)

    if "username" in updateData and updateData["username"] is not None:
        newUsername = updateData["username"]
        if isUsernameTaken(users, newUsername, exclude_user_id=userId):
            raise HTTPException(
                status_code=409, detail="Username already taken; retry."
            )

    if "pw" in updateData and updateData["pw"] is not None:
        updateData["pw"] = hashPassword(updateData["pw"])

    for index, current_user in enumerate(users):
        if current_user.id == userId:
            updated_user = current_user.model_copy(update=updateData)
            users[index] = updated_user
            saveUsers(users)
            return updated_user

    raise HTTPException(status_code=404, detail=f"User '{userId}' not found")


def deleteUser(userId: int):
    """
    Delete a user by ID

    Args:
        userId (int): ID of the user to delete
    Raises:
        HTTPException: user not found
    """
    users = loadUsers()

    for index, user in enumerate(users):
        if user.id == userId:
            del users[index]
            saveUsers(users)
            return

    raise HTTPException(status_code=404, detail=f"User '{userId}' not found")


def getUserByEmail(email: str) -> User | None:
    """
    Check if email exists
    
    Args:
        email (str): email to check
    """
    users = loadUsers()
    normalized = email.lower()
    for user in loadUsers():
        if user.email.lower() == normalized:
            return user
    return None


def generateResetToken(email: str) -> str:
    """Generate a temporary reset token"""
    token = secrets.token_hex(16)
    expires = int(time.time()) + 900  # expires in 15 min
    resetTokens[token] = {"email": email.lower(), "expires": expires}
    return token


def resetPassword(token: str, newPassword: str) -> bool:
    """Reset password if token valid"""
    data = resetTokens.get(token)
    if not data or data["expires"] < time.time():
        return False

    users = loadUsers()
    for user in users:
        if user.email.lower() == data["email"]:
            user.pw = hashPassword(newPassword.strip())
            saveUsers(users)
            del resetTokens[token]
            return True
    return False
