import pytest
import json
import fastapi
from fastapi.testclient import TestClient
from app.app import app
from ...schemas.user import User, UserCreate, UserUpdate
import tempfile
import builtins
from ..auth import(
     getAdminDashboard, 
     getCurrentUser, 
     getUserFromJson,
     decodeToken,
     requireAdmin,
     login
)


client = TestClient(app)

testUser = User(
    id = 10000,
    firstName = "somto",
    lastName = "azubuike",
    age = 20,
    email = "somto@gmail.com",
    username = "squig",
    pw = "password",
    role = "admin")

# unit tests

def test_getUsernameFromJsonDB(tmp_path, monkeypatch):
    users = [{"username": "squig", "pw": "password"}]
    filepath = tmp_path / "users.json"

    with open(filepath, "w") as file:
       json.dump(users, file)
    
    realOpen = builtins.open

    def fakeOpen(path, mode="r", *args, **kwargs):
       if path == "app/data/users.json":
           path = filepath
       return realOpen(path, mode, *args, **kwargs)
   
    monkeypatch.setattr(builtins, "open", fakeOpen)
    
    user = getUserFromJson("squig")
    assert user["username"] == "squig"

# def test_getAdminDashboard():
#     ans = getAdminDashboard()
#     assert ans == "in admin"