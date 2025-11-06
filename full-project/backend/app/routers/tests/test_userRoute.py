import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from app.routers.userRoute import router
from app.services import userService


@pytest.fixture
def app():
    app = FastAPI()
    app.include_router(router)
    return app


@pytest.fixture
def client(app):
    return TestClient(app)


@pytest.fixture
def mock_user(monkeypatch):
    """Mock user data at the service level (not repo directly)."""
    mock_users = [
        {
            "id": 1,
            "firstName": "Serena",
            "lastName": "Williams",
            "age": 30,
            "email": "serena@gmail.com",
            "username": "Serena",
            "pw": "hashedpass",
            "role": "employee",
        }
    ]

    # patch at the service level so routes use this
    monkeypatch.setattr("app.services.userService.loadAll", lambda: mock_users.copy())
    monkeypatch.setattr("app.services.userService.saveAll", lambda users: None)
    return mock_users


# TESTS FOR /users/forgot-password

def test_forgot_password_valid_email(client, mock_user):
    """Should generate a reset token for existing user"""
    response = client.post("/users/forgot-password", data={"email": "serena@gmail.com"})
    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert data["message"] == "Password reset link sent"


def test_forgot_password_invalid_email(client, mock_user):
    """Should return 404 for unknown email"""
    response = client.post("/users/forgot-password", data={"email": "unknown@gmail.com"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Email not found"


# TESTS FOR /users/reset-password

def test_reset_password_valid_token(client, mock_user):
    """Should reset password successfully using a valid token"""
    # generate token directly in service (same memory space)
    token = userService.generateResetToken("serena@gmail.com")

    # send reset request
    response = client.post("/users/reset-password", data={"token": token, "new_password": "newPass123"})
    assert response.status_code == 200
    assert response.json()["message"] == "Password reset successful"


def test_reset_password_invalid_token(client):
    """Should return 400 for invalid/expired token"""
    response = client.post("/users/reset-password", data={"token": "fakeToken123", "new_password": "anything"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid or expired token"
