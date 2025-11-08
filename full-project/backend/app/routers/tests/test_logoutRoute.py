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
    from app.routers import auth

    # Mock getCurrentUser to return a valid user
    def fake_get_current_user(username):
        return {"username": "testuser", "pw": "12345"}

    monkeypatch.setattr(auth, "getCurrentUser", fake_get_current_user)

    response = client.post("/login", data={"username": "testuser", "password": "12345"})
    assert response.status_code == 200
    assert "Welcome back" in response.json()["message"]


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
    assert "testuser" in body["message"]
