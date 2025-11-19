import secrets, time
from typing import List
from fastapi import HTTPException
from ..schemas.user import User, UserCreate, UserUpdate
from ..schemas.role import Role
from ..repos.userRepo import get_next_user_id, loadUsers, saveAll
from ..utilities.security import hashPassword, verifyPassword

reset_tokens = {}  # token -> {"email": str, "expires": int}


def is_username_taken(users: List[User], username: str) -> bool:
    """
    Check if a username already exists in the user list, case-insensitive.
    Assumes `username` is already Pydantic-validated and stripped.

    Example:
        "Ichigo76" and "ichigo76" are considered the same.
    """
    normalized_new_username = username.lower()

    for user in users:
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
        firstName=payload.firstName.strip(),
        lastName=payload.lastName.strip(),
        age=payload.age,
        email=payload.email,
        pw=hashed_pw,
    )

    users.append(new_user)
    saveAll(users)
    return new_user


def getUserById(userId: int) -> User:
    """Get a user by ID

    Returns:
        New user

    Raises:
        HTTPException: user not found
    """
    users = loadUsers()
    for u in users:
        if int(u.get("id")) == int(userId):
            return User(**u)
    raise HTTPException(status_code=404, detail=f"User '{userId}' not found")


def updateUser(userId: int, payload: UserUpdate) -> User:
    """
    Update user info while keeping ID type as int

    Returns:
        Updated user

    Raises:
        HTTPException: user not found
    """
    users = loadUsers()
    for idx, u in enumerate(users):
        if int(u.get("id")) == int(userId):
            current_user = User(**u)
            update_data = payload.model_dump(exclude_unset=True)

            updated_dict = current_user.model_dump()
            updated_dict.update(update_data)

            for field in ["firstName", "lastName", "email", "username", "pw"]:
                if field in update_data and updated_dict.get(field):
                    updated_dict[field] = updated_dict[field].strip()

            if "pw" in update_data and update_data["pw"]:
                updated_dict["pw"] = hashPassword(update_data["pw"])

            updated_user = User(**updated_dict)
            users[idx] = updated_user.model_dump()
            saveAll(users)
            return updated_user

    raise HTTPException(status_code=404, detail=f"User '{userId}' not found")


def deleteUser(userId: int) -> None:
    """Delete a user by ID"""
    users = loadUsers()
    new_users = [u for u in users if int(u.get("id")) != int(userId)]
    if len(new_users) == len(users):
        raise HTTPException(status_code=404, detail=f"User '{userId}' not found")
    saveAll(new_users)


# Password Reset
def emailExists(email: str) -> bool:
    """Check if email exists"""
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
