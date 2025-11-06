import pytest
import json
import fastapi
from fastapi.testclient import TestClient
from app.app import app
from ...schemas.user import User, UserCreate, UserUpdate
import tempfile
import builtins
from ..auth import (
    getUsernameFromJsonDB,
    decodeToken,
)
from ...repos.userRepo import loadAll  # Add this import
from unittest.mock import patch

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
    """Creates a fake open function that redirects app/data/users.json to our test file
    
    Returns:
        The fake open file path
    """
    realOpen = builtins.open

    def fakeOpen(path, mode="r", *args, **kwargs):
        if path.replace("\\", "/") == "app/data/users.json":
            return realOpen(filepath, mode, *args, **kwargs)
        return realOpen(path, mode, *args, **kwargs)
    
    return fakeOpen

# unit tests
@patch('app.repos.userRepo.loadAll')
def test_getUsernameFromJsonDB(mock_load):
    """Test that we can get a user from the JSON DB"""
    # Arrange
    mock_load.return_value = testUser

    # Act
    user = getUsernameFromJsonDB("squig")

    # Assert
    assert user is not None
    assert user == testUser[0]  # Compare with the first user in our test data
    mock_load.assert_called_once()

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
@patch('app.repos.userRepo.loadAll')
def test_validUserLogin(mock_load):
    """Test valid login credentials return proper token"""
    # Arrange
    mock_load.return_value = testUser

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