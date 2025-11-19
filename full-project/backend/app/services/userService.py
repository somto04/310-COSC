import secrets, time
from typing import List
from fastapi import HTTPException
from ..schemas.user import User, UserCreate, UserUpdate
from ..schemas.role import Role
from ..repos.userRepo import get_next_user_id, loadUsers, saveAll
from ..utilities.security import hashPassword, verifyPassword

reset_tokens = {}  # token -> {"email": str, "expires": int}


def is_username_taken(
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
    normalized_new_username = username.lower()

    for user in users:
        if exclude_user_id is not None and user.id == exclude_user_id:
            continue

        normalized_existing_username = user.username.lower()
        if normalized_existing_username == normalized_new_username:
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

    if is_username_taken(users, payload.username):
        raise HTTPException(status_code=409, detail="Username already taken; retry.")

    hashed_pw = hashPassword(payload.pw)

    new_user = User(
        id=get_next_user_id(),
        username=payload.username,
        firstName=payload.firstName,
        lastName=payload.lastName,
        age=payload.age,
        email=payload.email,
        pw=hashed_pw,
    )

    users.append(new_user)
    saveAll(users)
    return new_user


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
    update_data = payload.model_dump(exclude_unset=True)

    if "username" in update_data and update_data["username"] is not None:
        new_username = update_data["username"]
        if is_username_taken(users, new_username, exclude_user_id=userId):
            raise HTTPException(
                status_code=409, detail="Username already taken; retry."
            )

    if "pw" in update_data and update_data["pw"] is not None:
        update_data["pw"] = hashPassword(update_data["pw"])

    for index, current_user in enumerate(users):
        if current_user.id == userId:
            updated_user = current_user.model_copy(update=update_data)
            users[index] = updated_user
            saveAll(users)
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
            saveAll(users)
            return

    raise HTTPException(status_code=404, detail=f"User '{userId}' not found")


def get_user_by_email(email: str) -> User | None:
    """
    Check if email exists
    
    Args:
        email (str): email to check
    """
    users = loadUsers()

    

    return any(u["email"].lower() == email.lower() for u in users)


def generateResetToken(email: str) -> str:
    """Generate a temporary reset token"""
    token = secrets.token_hex(16)
    expires = int(time.time()) + 900  # expires in 15 min
    reset_tokens[token] = {"email": email.lower(), "expires": expires}
    return token


def resetPassword(token: str, new_password: str) -> bool:
    """Reset password if token valid"""
    data = reset_tokens.get(token)
    if not data or data["expires"] < time.time():
        return False

    users = loadUsers()
    for u in users:
        if u["email"].lower() == data["email"]:
            u["pw"] = hashPassword(new_password.strip())
            saveAll(users)
            del reset_tokens[token]
            return True
    return False
