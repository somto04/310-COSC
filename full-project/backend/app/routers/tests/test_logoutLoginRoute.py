import pytest
from fastapi.testclient import TestClient
from app.app import app

client = TestClient(app)


@pytest.fixture
def mock_user(monkeypatch):
    """Mock getCurrentUser to return a fake user dictionary."""
    from app.routers import auth

    def fake_get_current_user(token=None):
        return {"username": "testuser", "role": "admin"}

    monkeypatch.setattr(auth, "getCurrentUser", fake_get_current_user)


def test_login_valid(monkeypatch):
    """Should return success message when username and password are valid"""
    from app.routers import loginRoute
    from app.utilities import security

    # fake db lookup
    def fake_get_user(username):
        # simulate stored *hashed* password
        return {"username": "testuser", "pw": "$2b$12$FakeHashString1234567890"}

    # fake password verification always succeeds
    def fake_verify_password(plain, hashed):
        return True

    monkeypatch.setattr(loginRoute, "getUsernameFromJsonDB", fake_get_user)
    monkeypatch.setattr(loginRoute, "verifyPassword", fake_verify_password)

    response = client.post("/login", data={"username": "testuser", "password": "12345"})
    assert response.status_code == 200
    body = response.json()
    assert "Login successful" in body["message"]




def test_login_invalid(monkeypatch):
    """Should raise HTTP 401 when password is incorrect"""
    from app.routers import auth

    def fake_get_current_user(username):
        return {"username": "testuser", "pw": "wrongpw"}

    monkeypatch.setattr(auth, "getCurrentUser", fake_get_current_user)

    response = client.post("/login", data={"username": "testuser", "password": "12345"})
    assert response.status_code == 401
    assert "Invalid username or password" in response.json()["detail"]


def test_logout_success(mock_user):
    """Should return success message when logout is called by authenticated user"""
    response = client.post("/logout")
    assert response.status_code == 200
    body = response.json()
    assert "logged out successfully" in body["message"]
    assert "tester" in body["message"]
