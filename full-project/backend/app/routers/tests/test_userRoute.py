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
from app.routers.authRoute import getCurrentUser
from app.schemas.role import Role
from app.schemas.movie import Movie


@pytest.fixture
def app():
    """Create a FastApi instance for testing"""
    app = FastAPI()
    app.include_router(router)
    return app

@pytest.fixture
def client(app):
    """Create a test client for making HTTP requests"""
    #app.include_router(router)
    return TestClient(app)

@pytest.fixture
def sampleUsersPydantic():
    return [
        User(
            id=1,
            username='alicej',
            firstName='Alice',
            lastName='Johnson',
            age=25,
            email='alice@example.com',
            pw='SecureP@ss123',
            role=Role.USER,
            penalties=0,
            isBanned=False,
            watchlist=[]
        ),
        User(
            id=2,
            username='bobsmith',
            firstName='Bob',
            lastName='Smith',
            age=30,
            email='bob@example.com',
            pw='passwHOrd!@#234',
            role=Role.ADMIN,
            penalties=1,
            isBanned=False,
            watchlist=[1, 2]
        )
    ]

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
            "isBanned": False,         
            "watchlist": []
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
            "isBanned": False,
            "watchlist": [1, 2]

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
    assert data["firstName"] == "Alice"
    assert data["username"] == "alicej"
    assert data["isBanned"] is False

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

    #override dependency to simulate authenticated user
    from app.routers.authRoute import getCurrentUser
    client.app.dependency_overrides[getCurrentUser] = lambda: MagicMock(id=1)
    
    updatedUser = sampleUsers[0].copy()
    updatedUser.update(updatedUserPayload)
    mockUpdate.return_value = updatedUser

    response = client.put("/users/1", json=updatedUserPayload)

    client.app.dependency_overrides = {}

    assert response.status_code == 200

    data = response.json()
    assert data["firstName"] == "AliceUpdated"
    assert data["email"] == "aliceupdated@example.com"

    from app.schemas.user import UserUpdate
    mockUpdate.assert_called_once_with(1, UserUpdate(**updatedUserPayload))


@patch("app.routers.userRoute.deleteUser")
def test_deleteUser(mockDelete, client, sampleUsers):
    """Test DELETE /users/{id} admin only deletes a user"""
    from app.routers.authRoute import getCurrentUser
    
    adminModel = User(**sampleUsers[1])
    client.app.dependency_overrides[getCurrentUser] = lambda: adminModel

    mockDelete.return_value = None
    response = client.delete("/users/1")
    assert response.status_code == 204
    mockDelete.assert_called_once_with(1)

def test_getUserProfile(sampleUsersPydantic):
    """Gets the user profile based on the userId given"""
    main_app.app.dependency_overrides[getCurrentUser] = lambda: sampleUsersPydantic[0]
    client = TestClient(main_app.app)

    with patch("app.routers.userRoute.getUserById", return_value = sampleUsersPydantic[0]):
        response = client.get("/users/userProfile", params={"userId": 1})

    assert response.status_code == 200
    data = response.json()

    assert data["user"]["id"] == 1          
    assert data["user"]["username"] == "alicej"
    assert data["isOwner"] is True    

    main_app.app.dependency_overrides = {} 
def test_getUserWatchlist(sampleUsersPydantic):
    main_app.app.dependency_overrides[getCurrentUser] = lambda: sampleUsersPydantic[1]
    client = TestClient(main_app.app)

    with patch("app.routers.userRoute.getUserById", return_value=sampleUsersPydantic[1]):
        with patch("app.routers.userRoute.loadMovies", return_value=[
            Movie(id=1, 
                  title="Movie1", 
                  movieIMDb=8.0, 
                  movieGenre=["Action"], 
                  directors=["Director1"], 
                  mainstars=["Star1"], 
                  description="Desc1", 
                  datePublished="2020-01-01", 
                  duration=120),
            Movie(id=2, 
                  title="Movie2", 
                  movieIMDb=7.5, 
                  movieGenre=["Drama"], 
                  directors=["Director2"], 
                  mainstars=["Star2"], 
                  description="Desc2", 
                  datePublished="2021-01-01", 
                  duration=130)
                ]):
            response = client.get("/users/watchlist")

    assert response.status_code == 200
    data = response.json()
    assert [{"id": movie["id"], "title": movie["title"]} for movie in data["watchlist"]] == [
        {"id": 1, "title": "Movie1"},
        {"id": 2, "title": "Movie2"}
    ]
    main_app.app.dependency_overrides = {}

@patch("app.routers.userRoute.getUserById")
@patch("app.routers.userRoute.loadMovies")
@patch("app.routers.userRoute.updateUser")
def test_addMovieToWatchlist(mockUpdate, mockLoad, mockGet, client, sampleUsersPydantic):
    client.app.dependency_overrides[getCurrentUser] = lambda: MagicMock(id=1)

    user = sampleUsersPydantic[0]
    mockGet.return_value = user

    mockLoad.return_value = [
        Movie(
            id=1,
            title="Movie1",
            movieIMDb=8.0,
            movieGenre=["Action"],
            directors=["Director1"],
            mainstars=["Star1"],
            description="Desc1",
            datePublished="2020-01-01",
            duration=120
        ),
        Movie(
            id=2,
            title="Movie2",
            movieIMDb=7.5,
            movieGenre=["Drama"],
            directors=["Director2"],
            mainstars=["Star2"],
            description="Desc2",
            datePublished="2021-01-01",
            duration=130
        )
    ]

    movieId = 2
    response = client.post(f"/users/watchlist/{movieId}")
    assert response.status_code == 200

    updatedList = user.watchlist + [movieId]
    mockUpdate.assert_called_once_with(
        1,
        UserUpdate(watchlist=updatedList)
    )
    
@patch("app.routers.userRoute.getUserById")
@patch("app.routers.userRoute.loadMovies")
@patch("app.routers.userRoute.updateUser")
def test_removeMovieFromWatchlist(mockUpdate, mockLoad, mockGet, client, sampleUsers):
    client.app.dependency_overrides[getCurrentUser] = lambda: MagicMock(id=2, role="USER")

    user = sampleUsers[1]
    user["watchlist"] = [1, 2]
    mockGet.return_value = user

    mockLoad.return_value = [
        Movie(
            id=1,
            title="Movie1",
            movieIMDb=8.0,
            movieGenre=["Action"],
            directors=["Director1"],
            mainstars=["Star1"],
            description="Desc1",
            datePublished="2020-01-01",
            duration=120
        ),
        Movie(
            id=2,
            title="Movie2",
            movieIMDb=7.5,
            movieGenre=["Drama"],
            directors=["Director2"],
            mainstars=["Star2"],
            description="Desc2",
            datePublished="2021-01-01",
            duration=130
        )
    ]

    movieIdToRemove = 2
    response = client.delete(f"/users/watchlist/{movieIdToRemove}")
    assert response.status_code == 200

    expectedUpdatedList = [1]
    mockUpdate.assert_called_once_with(
        2,
        UserUpdate(watchlist=expectedUpdatedList)
    )
    assert response.json()["watchlist"] == expectedUpdatedList