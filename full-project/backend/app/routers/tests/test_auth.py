import pytest
from fastapi.testclient import TestClient

from app.app import app
from app.routers import auth
from app.schemas.user import (
    User,
    CurrentUser,
    Username,
    Password,
    Email,
)
from app.schemas.role import Role
from app.utilities.security import hashPassword
from app.services.authService import reset_tokens

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
    reset_tokens.clear()
    yield
    reset_tokens.clear()


# ======================================================================
# auth router tests (HTTP-level)
# ======================================================================

# ------------- LOGIN -------------


def testLoginSuccess(monkeypatch):
    """Valid username/password, non-banned user → 200 + success message."""
    user = makeUser()

    monkeypatch.setattr(auth, "getUserByUsername", lambda username: user)

    response = client.post(
        "/token",
        data={"username": VALID_USERNAME, "password": VALID_PASSWORD},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["message"] == "Login successful"
    assert body["access_token"] == VALID_USERNAME


def testLoginInvalidPassword(monkeypatch):
    """Wrong password → 401 from router validatePassword."""
    user = makeUser()

    monkeypatch.setattr(auth, "getUserByUsername", lambda username: user)

    response = client.post(
        "/token",
        data={"username": VALID_USERNAME, "password": "WrongPass999"},
    )

    assert response.status_code == 401
    assert "Invalid username or password" in response.json()["detail"]


def testLoginUserDoesNotExist(monkeypatch):
    """No such user → 401 from ensureUserExists."""
    monkeypatch.setattr(auth, "getUserByUsername", lambda username: None)

    response = client.post(
        "/token",
        data={"username": "NoSuchUser", "password": VALID_PASSWORD},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid username or password"


def testLoginBannedUser(monkeypatch):
    """Banned user → 403 even if credentials are correct."""
    bannedUser = makeUser(isBanned=True)

    monkeypatch.setattr(auth, "getUserByUsername", lambda username: bannedUser)

    response = client.post(
        "/token",
        data={"username": VALID_USERNAME, "password": VALID_PASSWORD},
    )

    assert response.status_code == 403
    assert "banned" in response.json()["detail"]


# ------------- LOGIN REQUEST VALIDATION (Annotated types) -------------


def testLoginValidationRejectsShortUsername():
    """Username shorter than MIN_USERNAME_LENGTH → 422."""
    response = client.post(
        "/token",
        data={"username": "ab", "password": VALID_PASSWORD},
    )

    assert response.status_code == 422


def testLoginValidationRejectsBadUsernameChars():
    """Username with invalid characters (space) → 422."""
    response = client.post(
        "/token",
        data={"username": "bad username", "password": VALID_PASSWORD},
    )

    assert response.status_code == 422


def testLoginValidationRejectsShortPassword():
    """Password shorter than MIN_PASSWORD_LENGTH → 422."""
    response = client.post(
        "/token",
        data={"username": VALID_USERNAME, "password": "short"},
    )

    assert response.status_code == 422


# ------------- LOGOUT -------------


def testLogoutSuccess(monkeypatch):
    """Authenticated user can logout → 200."""
    user = makeUser()
    current = makeCurrentUser(user)

    app.dependency_overrides[auth.getCurrentUser] = lambda: current

    response = client.post("/logout")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert "logged out successfully" in body["message"]
    assert user.username in body["message"]


def testLogoutUnauthorized(monkeypatch):
    """If getCurrentUser fails (no user), logout → 401."""
    # getUserByUsername returns None, so ensureUserExists will raise HTTPException(401)
    monkeypatch.setattr(auth, "getUserByUsername", lambda token: None)

    response = client.post(
        "/logout",
        headers={"Authorization": "Bearer invalidToken"},
    )

    assert response.status_code == 401


# ------------- ADMIN DASHBOARD -------------


def testAdminDashboardAllowed():
    """Admin role can access /adminDashboard → 200."""
    adminUser = makeUser(role=Role.ADMIN)
    current = makeCurrentUser(adminUser)

    app.dependency_overrides[auth.getCurrentUser] = lambda: current

    response = client.get("/adminDashboard")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["message"] == "Welcome to the admin dashboard"


def testAdminDashboardForbidden():
    """Non-admin role → 403."""
    normalUser = makeUser(role=Role.USER)
    current = makeCurrentUser(normalUser)

    app.dependency_overrides[auth.getCurrentUser] = lambda: current

    response = client.get("/adminDashboard")

    app.dependency_overrides.clear()

    assert response.status_code == 403
    assert response.json()["detail"] == "Admin privileges required"


# ------------- FORGOT PASSWORD -------------


def testForgotPasswordSuccess(monkeypatch):
    """Existing email → 200 + token returned."""
    user = makeUser()

    monkeypatch.setattr(auth, "getUserByEmail", lambda email: user)

    # use valid email to satisfy Email Annotated type
    response = client.post("/forgot-password", data={"email": VALID_EMAIL})

    assert response.status_code == 200
    body = response.json()
    assert body["message"] == "Password reset link sent"
    assert "token" in body


def testForgotPasswordEmailNotFound(monkeypatch):
    """Unknown email → 404."""
    monkeypatch.setattr(auth, "getUserByEmail", lambda email: None)

    response = client.post("/forgot-password", data={"email": VALID_EMAIL})

    assert response.status_code == 404
    assert response.json()["detail"] == "Email not found"


def testForgotPasswordInvalidEmailFormat():
    """Malformed email fails Email Annotated validation → 422."""
    response = client.post("/forgot-password", data={"email": "not-an-email"})

    assert response.status_code == 422


# ------------- RESET PASSWORD -------------


def testResetPasswordSuccess(monkeypatch):
    """resetPassword returns True → 200."""
    monkeypatch.setattr(auth, "resetPassword", lambda token, pw: True)

    response = client.post(
        "/reset-password",
        data={"token": "some-token", "new_password": VALID_PASSWORD},
    )

    assert response.status_code == 200
    assert "Password reset successful" in response.json()["message"]


def testResetPasswordInvalidOrExpired(monkeypatch):
    """resetPassword returns False → 400."""
    monkeypatch.setattr(auth, "resetPassword", lambda token, pw: False)

    response = client.post(
        "/reset-password",
        data={"token": "bad-token", "new_password": VALID_PASSWORD},
    )

    assert response.status_code == 400
    assert "Invalid or expired token" in response.json()["detail"]
