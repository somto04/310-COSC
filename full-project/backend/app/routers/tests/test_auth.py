import pytest
import json
import fastapi
from fastapi.testclient import TestClient
from app.app import app
from ...repos import userRepo
from ...schemas.user import User, UserCreate, UserUpdate
import app.routers.auth as auth
from ..auth import(
     getUsernameFromJsonDB,
     decodeToken,
)

client = TestClient(app)

# Test data
testUsers = [
    {
        "username": "squig",
        "pw": "password",
        "role": "admin",
        "userId": 1
    },
    {
        "username": "somto",
        "pw": "password",
        "role": "user",
        "userId": 2
    }
]

# unit tests
def test_getUsernameFromJsonDB(monkeypatch):   
    monkeypatch.setattr(auth, "loadAll", lambda: testUsers)

    user = getUsernameFromJsonDB("squig")
    assert user is not None
    assert user["username"] == "squig"

def test_getInvalidUsernameFromJsonDB(monkeypatch):   
    monkeypatch.setattr(auth, "loadAll", lambda: testUsers)

    user = getUsernameFromJsonDB("No user")
    assert user is None

def test_decodeToken(monkeypatch):
    monkeypatch.setattr(auth, "loadAll", lambda: testUsers)

    expected = {
        "username": "squig",
        "pw": "password",
        "role": "admin",
        "userId": 1
    }
    assert decodeToken("squig") == expected

# intergration tests
def test_validUserLogin(monkeypatch):
    monkeypatch.setattr(auth, "loadAll", lambda: testUsers)

    response = client.post("/token", data={"username": "squig", "password": "password"})
    assert response.status_code == 200
    data = response.json()
    assert data["access_token"] == "squig"
    assert data["role"] == "admin"

def test_invalidUserLoginWrongPw(monkeypatch):
    monkeypatch.setattr(auth, "loadAll", lambda: testUsers)

    response = client.post("/token", data={"username": "squig", "password": "pw"})
    assert response.status_code == 401

def test_getAdminDashboard(monkeypatch):
    monkeypatch.setattr(auth, "loadAll", lambda: testUsers)
    
    response = client.get("/adminDashboard", headers={"Authorization": "Bearer squig"})
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "in admin"

def test_getAdminDashboardInvalidUser(monkeypatch):
    monkeypatch.setattr(auth, "loadAll", lambda: testUsers)
    
    response = client.get("/adminDashboard", headers={"Authorization": "Bearer somto"})
    assert response.status_code == 403


