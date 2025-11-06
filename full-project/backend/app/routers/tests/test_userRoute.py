"""
Integration and Unit Tests for User Router

This file contains:
1. Unit tests - Test individual service functions in isolation
2. Integration tests - Test the API endpoints with FastAPI TestClient
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI, status, HTTPException
from unittest.mock import patch
from app.app import app
from app.routers.userRoute import router
from app.schemas.user import User, UserCreate, UserUpdate


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
def sample_users():
    """Sample user data for tests"""
    return [
        {
            "id": 1,
            "firstName": "Alice",
            "lastName": "Johnson",
            "age": 25,
            "email": "alice@example.com",
            "username": "alicej",
            "pw": "secret123",
            "role": "user"
        },
        {
            "id": 2,
            "firstName": "Bob",
            "lastName": "Smith",
            "age": 30,
            "email": "bob@example.com",
            "username": "bobsmith",
            "pw": "password",
            "role": "admin"
        } 
    ]

@pytest.fixture
def new_user_payload():
    """Sample user payload creation"""
    return {
        "firstName": "Charlie",
        "lastName": "Brown",
        "age": 22,
        "email": "Charlie@example.com",
        "username": "snoopyfan123",
        "pw": "password",
        "role": "user"
    }
    
@pytest.fixture
def updated_user_payload():
    """Sample update payload following UserUpdate schema"""
    return {
        "firstName": "AliceUpdated",
        "email": "aliceupdated@example.com",
        "age": 26
    }
    
#tests

@patch("app.routers.userRoute.listUsers")
def test_get_all_users(mock_list, client, sample_users):
    """Test GET /users returns all users"""
    mock_list.return_value = sample_users
    response = client.get("/users")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["username"] == "alicej"
    mock_list.assert_called_once()
    
@patch("app.routers.userRoute.createUser")
def test_create_user(mock_create, client, new_user_payload):
    """Test POST /users creates a user"""
    mock_create.return_value = {
        "id": 3,
        **new_user_payload
    } 
    response = client.post("/users", json=new_user_payload)
    assert response.status_code == 201 
    data = response.json()
    assert data["username"] == "snoopyfan123"
    assert data ["role"] == "user"
    assert data["age"] >= 16
    mock_create.assert_called_once()
    
@patch("app.routers.userRoute.getUserById")
def test_get_user_by_id(mock_get, client, sample_users):
    """Test GET /users/{id} returns the correct user"""
    mock_get.return_value = sample_users[0]
    response = client.get("/users/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["username"] == "alicej"
    mock_get.assert_called_once_with("1")

@patch("app.routers.userRoute.updateUser")
def test_update_user(mock_update, client, sample_users, updated_user_payload):
    """Test PUT /users/{id} updates user info"""
    updated_user = sample_users[0].copy()
    updated_user.update(updated_user_payload)
    mock_update.return_value = updated_user
    response = client.put("/users/1", json=updated_user_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["firstName"] == "AliceUpdated"
    assert data["email"] == "aliceupdated@example.com"
    
    from app.schemas.user import UserUpdate
    mock_update.assert_called_once_with("1", UserUpdate(**updated_user_payload))

@patch("app.routers.userRoute.deleteUser")
def test_delete_user(mock_delete, client):
    """Test DELETE /users/{id} deletes a user"""
    mock_delete.return_value = None
    response = client.delete("/users/1")
    assert response.status_code == 204
    mock_delete.assert_called_once_with("1")
            