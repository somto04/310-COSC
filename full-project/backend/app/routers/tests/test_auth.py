import pytest
import fastapi
from fastapi.testclient import TestClient
from app.app import app
from ...schemas.user import User, UserCreate, UserUpdate
from ..auth import(
     getAdminDashboard, 
     getCurrentUser, 
     getUsernameFromJsonDB,
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

#def test_getUsernameFromJsonDB():
    

def test_getAdminDashboard():
    ans = getAdminDashboard()
    assert ans == {"message": "Welcome to the admin dashboard"}