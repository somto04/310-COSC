import time
import pytest
from fastapi.testclient import TestClient

from app.app import app
from app.schemas.user import (
    User,
    CurrentUser,
    Username,
    Password,
    Email,
)
from app.schemas.role import Role
from app.utilities.security import hashPassword
from app.services.authService import (
    validatePassword as serviceValidatePassword,
    ensureUserExists as serviceEnsureUserExists,
    generateResetToken,
    resetPassword,
    UserNotFoundError,
    InvalidPasswordError,
    resetTokens,
)
from app.services import authService
from app.repos import userRepo


# ======================================================================
# Common helpers / fixtures
# ======================================================================

client = TestClient(app)

VALID_USERNAME: Username = "validUser_01"
VALID_PASSWORD: Password = "ValidPass123"
VALID_EMAIL: Email = "valid.user@example.com"


def makeUser(
    *,
    userId: int = 1,
    username: str = VALID_USERNAME,
    rawPassword: str = VALID_PASSWORD,
    role: Role = Role.USER,
    email: str = VALID_EMAIL,
    isBanned: bool = False,
) -> User:
    """Create a User instance with a properly hashed pw and valid fields."""
    return User(
        id=userId,
        username=username,
        pw=hashPassword(rawPassword),
        role=role,
        email=email,
        age=25,
        firstName="Test",
        lastName="User",
        penalties=0,
        isBanned=isBanned,
    )


def makeCurrentUser(user: User) -> CurrentUser:
    return CurrentUser(
        id=user.id,
        username=user.username,
        role=user.role,
    )


@pytest.fixture(autouse=True)
def clearResetTokens():
    """Ensure reset_tokens is clean for each test."""
    resetTokens.clear()
    yield
    resetTokens.clear()


# ======================================================================
# authService tests (domain-level)
# ======================================================================


def testEnsureUserExistsReturnsUser():
    user = makeUser()
    assert serviceEnsureUserExists(user) is user


def testEnsureUserExistsRaisesForNone():
    with pytest.raises(UserNotFoundError):
        serviceEnsureUserExists(None)


def testValidatePasswordCorrect():
    user = makeUser()
    # should not raise for the correct password
    serviceValidatePassword(user, VALID_PASSWORD)


def testValidatePasswordIncorrect():
    user = makeUser()
    with pytest.raises(InvalidPasswordError):
        serviceValidatePassword(user, "WrongPassword999")


def testGenerateResetTokenStoresData():
    token = generateResetToken(VALID_EMAIL)

    assert token in resetTokens
    data = resetTokens[token]
    assert data["email"] == VALID_EMAIL.lower()
    assert isinstance(data["expires"], int)


def testResetPasswordSuccess(monkeypatch):
    user = makeUser()
    oldPwHash = user.pw

    token = generateResetToken(user.email)

    def fakeLoadUsers():
        return [user]

    savedUsers = {}

    def fakeSaveUsers(users):
        savedUsers["users"] = users

    monkeypatch.setattr("app.services.authService.loadUsers", fakeLoadUsers)
    monkeypatch.setattr("app.services.authService.saveUsers", fakeSaveUsers)

    result = resetPassword(token, "AnotherPass123")

    assert result is True
    # password hash should have changed from the old value
    assert savedUsers["users"][0].pw != oldPwHash


def testResetPasswordFailsForExpiredToken(monkeypatch):
    user = makeUser()
    token = generateResetToken(user.email)

    # force expiration in the past
    resetTokens[token]["expires"] = int(time.time()) - 10

    monkeypatch.setattr(userRepo, "loadUsers", lambda: [user])
    monkeypatch.setattr(userRepo, "saveUsers", lambda users: None)

    result = resetPassword(token, "NewPass123")
    assert result is False


def testResetPasswordFailsForMissingToken(monkeypatch):
    user = makeUser()

    monkeypatch.setattr(userRepo, "loadUsers", lambda: [user])
    monkeypatch.setattr(userRepo, "saveUsers", lambda users: None)

    result = resetPassword("nonexistent-token", "NewPass123")
    assert result is False


def testResetPasswordFailsWhenEmailNotFound(monkeypatch):
    token = generateResetToken(VALID_EMAIL)

    # No users match this email
    monkeypatch.setattr(userRepo, "loadUsers", lambda: [])
    monkeypatch.setattr(userRepo, "saveUsers", lambda users: None)

    result = resetPassword(token, "NewPass123")

    assert result is False
    # token should still exist since no user was updated
    assert token in resetTokens
