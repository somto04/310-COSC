"""
Integration and Unit Tests for User Router

This file contains:
1. Unit tests - Test individual service functions in isolation
2. Integration tests - Test the API endpoints with FastAPI TestClient
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI, status, HTTPException
from unittest.mock import patch, MagicMock
from app.app import app
from app import app as main_app
from app.routers.userRoute import router
from app.schemas.user import User, UserCreate, UserUpdate
from ..userRoute import getUserProfile
from app.routers.auth import getCurrentUser
from app.schemas.role import Role


@pytest.fixture
def app():
    """Create a FastApi instance for testing"""
    app = FastAPI()
    app.include_router(router)
    return app

@pytest.fixture
def client(app):
    """Create a test client for making HTTP requests"""
    app.include_router(router)
    return TestClient(app)

@pytest.fixture
def sampleUsers():
    """Sample user data for tests"""
    return [
        {
            "id": 1,
            "firstName": "Alice",
            "lastName": "Johnson",
            "age": 25,
            "email": "alice@example.com",
            "username": "alicej",
            "pw": "SecureP@ss123",
            "role": Role.USER, 
            "penalties": 0,
            "isBanned": False
        },
        {
            "id": 2,
            "firstName": "Bob",
            "lastName": "Smith",
            "age": 30,
            "email": "bob@example.com",
            "username": "bobsmith",
            "pw": "passwHOrd!@#234",
            "role": Role.ADMIN,
            "penalties": 1,
            "isBanned": False
        } 
    ]

@pytest.fixture
def newUserPayload():
    """Sample user payload creation"""
    return {
        "firstName": "Charlie",
        "lastName": "Brown",
        "age": 22,
        "email": "Charlie@example.com",
        "username": "snoopyfan123",
        "pw": "MyP@ssword456",
    }
    
@pytest.fixture
def updatedUserPayload():
    """Sample update payload following UserUpdate schema"""
    return {
        "firstName": "AliceUpdated",
        "email": "aliceupdated@example.com",
        "age": 26
    }
    
#tests

@patch("app.routers.userRoute.listUsers")
def test_getAllUsers(mockList, client, sampleUsers):
    """Test GET /users returns all users"""
    mockList.return_value = sampleUsers
    response = client.get("/users")
    assert response.status_code == 200
    data = response.json()
    
    assert len(data) == 2
    assert data[0]["username"] == "alicej"
    assert data[0]["id"] == 1
    assert data[0]["firstName"] == "Alice"
    assert data[0]["isBanned"] is False

    # SafeUser check - sensitive fields should not be present
    for user in data:
        assert "email" not in user
        assert "pw" not in user
        assert "age" not in user
        assert "lastName" not in user
        assert "role" not in user
        assert "penalties" not in user
    mockList.assert_called_once()
    
@patch("app.routers.userRoute.createUser")
def test_createUser(mockCreate, client, newUserPayload):
    """Test POST /users creates a user"""
    mockCreate.return_value = {
        "id": 3,
        **newUserPayload
    } 
    response = client.post("/users", json=newUserPayload)
    assert response.status_code == 201 
    data = response.json()
    assert data["username"] == "snoopyfan123"
    assert data ["role"] == Role.USER
    assert data["age"] >= 16
    mockCreate.assert_called_once()
    
@patch("app.routers.userRoute.getUserById")
def test_getUserById(mockGet, client, sampleUsers):
    """Test GET /users/{id} returns the correct user"""
    mockGet.return_value = sampleUsers[0]
    response = client.get("/users/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data[0]["firstName"] == "Alice"
    assert data[0]["username"] == "alicej"
    assert data[0]["isBanned"] is False

    for user in data:
        assert "email" not in user
        assert "pw" not in user
        assert "age" not in user
        assert "lastName" not in user
        assert "role" not in user
        assert "penalties" not in user
    
    mockGet.assert_called_once_with(1)

@patch("app.routers.userRoute.updateUser")
def test_updateUser(mockUpdate, client, sampleUsers, updatedUserPayload):
    """Test PUT /users/{id} updates user info"""
    updatedUser = sampleUsers[0].copy()
    updatedUser.update(updatedUserPayload)
    mockUpdate.return_value = updatedUser
    response = client.put("/users/1", json=updatedUserPayload)
    assert response.status_code == 200
    data = response.json()
    assert data["firstName"] == "AliceUpdated"
    assert data["email"] == "aliceupdated@example.com"
    
    from app.schemas.user import UserUpdate
    mockUpdate.assert_called_once_with(1, UserUpdate(**updatedUserPayload))

@patch("app.routers.userRoute.deleteUser")
def test_deleteUser(mockDelete, client):
    """Test DELETE /users/{id} deletes a user"""
    mockDelete.return_value = None
    response = client.delete("/users/1")
    assert response.status_code == 204
    mockDelete.assert_called_once_with(1)

def fakeGetCurrentUser():
    return MagicMock(id=1)

def test_getUserProfile(sampleUsers):
    """Gets the user profile based on the userId given"""
    main_app.app.dependency_overrides[getCurrentUser] = fakeGetCurrentUser
    client = TestClient(main_app.app)
    with patch("app.routers.userRoute.getUserById", return_value = sampleUsers[0]):
        response = client.get("/users/userProfile/1")

    assert response.status_code == 200
    data = response.json()

    assert data["user"]["id"] == 1          
    assert data["user"]["username"] == "alicej"
    assert data["isOwner"] is True    

    main_app.app.dependency_overrides = {} 