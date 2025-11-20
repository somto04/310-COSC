import pytest
import json
import fastapi
from fastapi.testclient import TestClient
from app.app import app
from ...schemas.user import User
from ...repos import userRepo
from ...schemas.user import CurrentUser
import app.routers.auth as auth
from ..auth import getUsernameFromJsonDB
from ...schemas.role import Role

client = TestClient(app)

def fakeGetCurrentAdmin(token=None):
        return CurrentUser(
            id=1,
            username="testUser",
            role=Role.ADMIN
        )

def fakeLoadUsers():
    return [
        User(
            id=1,
            username="testUser",
            pw="password",
            role=Role.ADMIN,
            email="testuser@example.com",
            age=30,
            firstName="Test",
            lastName="User",
            penalties=0,
            isBanned=False,
        ), 
        User(
            id=2,
            username="anotherUser",
            pw="password2",
            role=Role.USER,
            email="anotheruser@example.com",
            age=25,
            firstName="Another",
            lastName="User",
            penalties=0,
            isBanned=False,
        )
    ]

def fake_get_current_user(token=None):
    return User(
        id=1,
        username="testuser",
        pw="HashedPassword21",
        role=Role.ADMIN,
        email="testuser@example.com",
        age=30,
        firstName="Test",
        lastName="User",
        penalties=0,
        isBanned=False,
    )
    
# unit tests
def test_getUsernameFromJsonDB(monkeypatch):
    """Should return a matching user when username exists"""
    from app.routers import auth   

    monkeypatch.setattr(auth, "loadUsers", fakeLoadUsers)

    user = getUsernameFromJsonDB("testUser")
    assert user is not None
    assert user.username == "testUser"


def test_getInvalidUsernameFromJsonDB(monkeypatch):
    """Should return None when username does not exist"""
    from app.routers import auth

    monkeypatch.setattr(auth, "loadUsers", fakeLoadUsers)

    user = getUsernameFromJsonDB("nouser")
    assert user is None


def test_login_valid(monkeypatch):
    """Should return success message when username and password are valid"""
    from app.routers import auth as loginRoute
    from app.utilities import security

    def fake_get_user(username):
        # simulate stored *hashed* password
        return {"username": "testuser", "pw": "$2b$12$FakeHashString1234567890"}

    def fake_verify_password(plain, hashed):
        return True

    monkeypatch.setattr(loginRoute, "getUsernameFromJsonDB", fake_get_user)
    monkeypatch.setattr(loginRoute, "verifyPassword", fake_verify_password)

    response = client.post("/token", data={"username": "testuser", "password": "12345"})
    assert response.status_code == 200
    body = response.json()
    assert "Login successful" in body["message"]


def test_login_invalid(monkeypatch):
    """Should raise HTTP 401 when password is incorrect"""
    from app.routers import auth

    def fake_get_current_user(username):
        return {"username": "testuser", "pw": "wrongpw"}

    monkeypatch.setattr(auth, "getCurrentUser", fake_get_current_user)

    response = client.post("/token", data={"username": "testuser", "password": "12345"})
    assert response.status_code == 401
    assert "This user does not exist" in response.json()["detail"]


def test_logout_success(monkeypatch):
    """Should return success message when logout is called by authenticated user"""
    from app.routers import auth

    fakeUser = CurrentUser(id=1, username="tester", role=Role.USER)
    monkeypatch.setattr(auth, "getUsernameFromJsonDB", lambda username: fakeUser)

    headers = {"Authorization": "Bearer tester"}
    response = client.post("/logout", headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert "logged out successfully" in body["message"]
    assert "tester" in body["message"]


def test_getAdminDashboard(monkeypatch):
    from app.routers import auth

    monkeypatch.setattr(auth, "loadUsers", fakeGetCurrentAdmin)

    client.headers.update({"Authorization": "Bearer tester"})
    response = client.get("/adminDashboard", headers={"Authorization": "Bearer testUser"})
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Welcome to the admin dashboard"
