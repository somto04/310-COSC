import secrets, time
from typing import List
from fastapi import HTTPException
from ..schemas.user import User, UserCreate, UserUpdate
from ..repos.userRepo import loadAll, saveAll
from ..utilities.security import hashPassword, verifyPassword

# in-memory reset tokens
reset_tokens = {}  # token -> {"email": str, "expires": int}

# CRUD Operations


def listUsers() -> List[User]:
    """Return all users as User objects"""
    return [User(**it) for it in loadAll()]


def createUser(payload: UserCreate) -> User:
    """Create a new user with a unique integer ID"""
    users = loadAll()
    unique_username = payload.username.strip()

    # Get next integer ID safely
    new_id = max([int(u.get("id", 0)) for u in users], default=0) + 1

    # Check for username duplicates (case insensitive)
    if any(u.get("username", "").strip().lower() == unique_username.lower() for u in users):
        raise HTTPException(status_code=409, detail="Username already taken; retry.")

    # Hash the password before saving
    hashed_pw = hashPassword(payload.pw.strip())

    new_user = User(
        id=new_id,
        firstName=payload.firstName.strip(),
        lastName=payload.lastName.strip(),
        age=payload.age,
        email=payload.email.strip(),
        username=unique_username,
        pw=hashed_pw,
        role=payload.role,
    )

    users.append(new_user.model_dump())
    saveAll(users)
    return new_user


def getUserById(userId: int) -> User:
    """Get a user by integer ID"""
    users = loadAll()
    for u in users:
        if int(u.get("id")) == int(userId):
            return User(**u)
    raise HTTPException(status_code=404, detail=f"User '{userId}' not found")


def updateUser(userId: int, payload: UserUpdate) -> User:
    """Update user info while keeping ID type as int"""
    users = loadAll()
    for idx, u in enumerate(users):
        if int(u.get("id")) == int(userId):
            current_user = User(**u)
            update_data = payload.model_dump(exclude_unset=True)

            updated_dict = current_user.model_dump()
            updated_dict.update(update_data)

            # Strip strings safely
            for field in ["firstName", "lastName", "email", "username", "pw"]:
                if field in update_data and updated_dict.get(field):
                    updated_dict[field] = updated_dict[field].strip()

            # Re-hash password if it's being updated
            if "pw" in update_data and update_data["pw"]:
                updated_dict["pw"] = hashPassword(update_data["pw"])

            updated_user = User(**updated_dict)
            users[idx] = updated_user.model_dump()
            saveAll(users)
            return updated_user

    raise HTTPException(status_code=404, detail=f"User '{userId}' not found")


def deleteUser(userId: int) -> None:
    """Delete a user by ID"""
    users = loadAll()
    new_users = [u for u in users if int(u.get("id")) != int(userId)]
    if len(new_users) == len(users):
        raise HTTPException(status_code=404, detail=f"User '{userId}' not found")
    saveAll(new_users)


# Password Reset


def emailExists(email: str) -> bool:
    """Check if email exists"""
    users = loadAll()
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

    users = loadAll()
    for u in users:
        if u["email"].lower() == data["email"]:
            u["pw"] = hashPassword(new_password.strip())
            saveAll(users)
            del reset_tokens[token]
            return True
    return False
