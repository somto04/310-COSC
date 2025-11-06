import pytest
import json
import fastapi
from fastapi.testclient import TestClient
from app.app import app
from ...schemas.user import User, UserCreate, UserUpdate
import tempfile
import builtins
from ..auth import(
     getUsernameFromJsonDB,
     decodeToken,
)

client = TestClient(app)

# Test data
testUser = [
    {
        "username": "squig",
        "pw": "password",
        "role": "admin",
        "userId": 1
    }
]

def getFakeOpen(filepath):
    realOpen = builtins.open

    def fakeOpen(path, mode="r", *args, **kwargs):
       if path == "app/data/users.json":
           path = filepath
       return realOpen(path, mode, *args, **kwargs)
    
    return fakeOpen

# unit tests
def test_getUsernameFromJsonDB(tmp_path, monkeypatch):
    filepath = tmp_path / "users.json"

    with open(filepath, "w") as file:
       json.dump(testUser, file)
    
    fakeOpen = getFakeOpen(filepath)    
    monkeypatch.setattr(builtins, "open", fakeOpen)

    user = getUsernameFromJsonDB("squig")
    assert user["username"] == "squig"

def test_decodeToken(tmp_path, monkeypatch):
    filepath = tmp_path / "users.json"

    with open(filepath, "w") as file:
       json.dump(testUser, file)
    
    fakeOpen = getFakeOpen(filepath)    
    monkeypatch.setattr(builtins, "open", fakeOpen)

    expected = {
        "username": "squig",
        "pw": "password",
        "role": "admin",
        "userId": 1
    }
    assert decodeToken("squig") == expected

# intergration tests
def test_validUserLogin(monkeypatch, tmp_path):
    """Test valid login credentials return proper token"""
    # Arrange
    filepath = tmp_path / "users.json"
    with open(filepath, "w") as file:
       json.dump(testUser, file)
    
    fakeOpen = getFakeOpen(filepath)    
    monkeypatch.setattr(builtins, "open", fakeOpen)

    # Act
    response = client.post(
        "/token",
        data={
            "username": "squig",
            "password": "password"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["access_token"] == "squig"
    assert data["token_type"] == "bearer"
    assert data["role"] == "admin"

def test_getAdminDashboard(monkeypatch, tmp_path):
    filepath = tmp_path / "users.json"

    with open(filepath, "w") as file:
       json.dump(testUser, file)

    fakeOpen = getFakeOpen(filepath)    
    monkeypatch.setattr(builtins, "open", fakeOpen)

    response = client.get("/adminDashboard", headers={"Authorization": "Bearer squig"})
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "in admin"


