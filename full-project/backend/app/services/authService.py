import secrets, time
from typing import TypedDict

from app.schemas.user import User, Password, Email
from app.utilities.security import verifyPassword, hashPassword
from app.repos.userRepo import loadUsers, saveUsers


class ResetTokenData(TypedDict):
    email: Email
    expires: int


resetTokens: dict[str, ResetTokenData] = {}  # token -> {"email": str, "expires": int}


class AuthenticationError(Exception):
    pass


class UserNotFoundError(AuthenticationError):
    pass


class InvalidPasswordError(AuthenticationError):
    pass


def validatePassword(user: User, password: Password) -> None:
    """
    Validate a user's password against the stored hashed password.

    Raises:
        InvalidPasswordError: If the password is incorrect.
    """
    if not verifyPassword(password, user.pw):
        raise InvalidPasswordError("Invalid password")


def ensureUserExists(user: User | None) -> User:
    """
    if the user exists, return it; otherwise, raise an error.

    Raises:
        UserNotFoundError: If the user does not exist.
    """
    if user is None:
        raise UserNotFoundError("User does not exist")
    return user


def generateResetToken(email: Email) -> str:
    """Generate a temporary reset token"""
    token = secrets.token_hex(16)
    expires = int(time.time()) + 900  # expires in 15 min
    resetTokens[token] = {"email": email, "expires": expires}
    return token


def resetPassword(token: str, new_password: Password) -> bool:
    """Reset password if token valid"""
    data = resetTokens.get(token)
    if not data or data["expires"] < time.time():
        return False

    users = loadUsers()
    for user in users:
        if user.email == data["email"]:
            user.pw = hashPassword(new_password)
            saveUsers(users)
            del resetTokens[token]
            return True
    return False
