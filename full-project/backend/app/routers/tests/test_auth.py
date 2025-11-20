import pytest
import json
import fastapi
from fastapi.testclient import TestClient
from app.app import app
from ...repos import userRepo
from ...schemas.user import User, UserCreate, UserUpdate
import app.routers.auth as auth
from ..auth import getUsernameFromJsonDB

client = TestClient(app)

@pytest.fixture
def mock_user(monkeypatch):
    """Mock getCurrentUser to return a fake user dictionary."""
    from app.routers import auth

    def fake_get_current_user(token=None):
        return {"username": "testuser", "role": "admin"}

    monkeypatch.setattr(auth, "getCurrentUser", fake_get_current_user)

# unit tests
def test_getUsernameFromJsonDB(monkeypatch):
    """Should return a matching user when username exists"""
    from app.routers import auth

    # Fake loadAll() returns a mock "database" of users
    def fake_loadAll():
        return [
            {"username": "testUser", "pw": "password", "role": "admin", "userId": 1},
            {"username": "other", "pw": "1234", "role": "user", "userId": 2},
        ]

    monkeypatch.setattr(auth, "loadAll", fake_loadAll)

    user = getUsernameFromJsonDB("testUser")
    assert user is not None
    assert user["username"] == "testUser"


def test_getInvalidUsernameFromJsonDB(monkeypatch):
    """Should return None when username does not exist"""
    from app.routers import auth

    def fake_loadAll():
        return [
            {"username": "testUser", "pw": "password", "role": "admin", "userId": 1},
        ]

    monkeypatch.setattr(auth, "loadAll", fake_loadAll)

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

    fake_user = {"userId": 1, "username": "tester", "role": "user"}
    monkeypatch.setattr(auth, "getUsernameFromJsonDB", lambda username: fake_user)

    headers = {"Authorization": "Bearer tester"}
    response = client.post("/logout", headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert "logged out successfully" in body["message"]
    assert "tester" in body["message"]

def test_getAdminDashboard(monkeypatch):
    from app.routers import auth

    def fake_loadAll():
        return [
            {"username": "tester", "pw": "password", "role": "admin", "userId": 1}
        ]

    monkeypatch.setattr(auth, "loadAll", fake_loadAll)

    response = client.get("/adminDashboard", headers={"Authorization": "Bearer tester"})
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Welcome to the admin dashboard"
