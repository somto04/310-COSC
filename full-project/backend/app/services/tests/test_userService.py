import pytest
import uuid
from fastapi import HTTPException
from unittest.mock import patch
from app.services import userService
from app.schemas.user import User, UserCreate, UserUpdate
from app.schemas.role import Role
from app.utilities.security import verifyPassword
from app.services.userService import UserNotFoundError, UsernameTakenError, EmailTakenError


# these fixtures provide mock user data for testing that follows our user schema
@pytest.fixture
def fakeUsers():
    return [
        User(
            id=1,
            firstName="Alex",
            lastName="Mason",
            age=25,
            email="alex@example.com",
            username="alexm",
            pw="hashed_pw_1",
            role=Role.USER,
        ),
        User(
            id=2,
            firstName="Jade",
            lastName="Taylor",
            age=30,
            email="jade@example.com",
            username="jadet",
            pw="hashed_pw_2",
            role=Role.ADMIN,
        ),
    ]


# this tests that all users currently stored are listed correctly
@patch("app.services.userService.loadUsers")
def test_listUsers(mockLoad, fakeUsers):
    mockLoad.return_value = fakeUsers
    result = userService.listUsers()
    assert len(result) == 2
    assert all(isinstance(user, User) for user in result)


# this tests that a new user is created and saved correctly according to our schema
@patch("app.services.userService.getNextUserId", return_value=3)
@patch("app.services.userService.saveUsers")
@patch("app.services.userService.loadUsers")
def test_createUser(mockLoad, mockSave, mockGetId, fakeUsers):
    mockLoad.return_value = list(fakeUsers)

    payload = UserCreate(
        firstName="Sam",
        lastName="Hill",
        age=22,
        email="sam@example.com",
        username="samh",
        pw="SecureP@ss123",
    )

    newUser = userService.createUser(payload)
    assert newUser.firstName == "Sam"
    assert newUser.username == "samh"
    assert newUser.id == 3
    assert newUser.pw != payload.pw
    assert newUser.pw.startswith("$2")
    mockSave.assert_called_once()

    args, kwargs = mockSave.call_args
    savedUsers = args[0]

    assert len(savedUsers) == 3 
    assert savedUsers[-1] == newUser
    assert isinstance(savedUsers[-1], User)



@patch("app.services.userService.saveUsers")
@patch("app.services.userService.loadUsers")
def test_createUserHashesPassword(mockLoad, mockSave, fakeUsers):
    mockLoad.return_value = fakeUsers

    plainPw = "Pass123A"
    payload = UserCreate(
        username="newuser",
        firstName="Sam",
        lastName="Hill",
        age=22,
        email="sam@example.com",
        pw=plainPw,
    )

    newUser = userService.createUser(payload)

    # 1. Should not store raw password
    assert newUser.pw != plainPw

    # 2. Hash should actually verify
    assert verifyPassword(plainPw, newUser.pw)

    # 3. Still only one save
    mockSave.assert_called_once()

    # 4. check what got saved
    savedUsers = mockSave.call_args[0][0]
    assert savedUsers[-1].pw == newUser.pw


@patch("app.services.userService.loadUsers")
def test_createUserUsernameTaken(mockLoad, fakeUsers):
    mockLoad.return_value = fakeUsers

    payload = UserCreate(
        firstName="Alex",
        lastName="Mason",
        age=25,
        email="alex@example.com",
        username="alexm",
        pw="SomePassword123",
    )

    with pytest.raises(userService.UsernameTakenError):
        userService.createUser(payload)


# this tests that a user can be retrieved by their ID correctly
@patch("app.services.userService.loadUsers")
def test_getUserByIdFound(mockLoad, fakeUsers):
    mockLoad.return_value = fakeUsers
    result = userService.getUserById(1)
    assert result.username == "alexm"


# this tests that an error is raised when trying to get a user that does not exist
@patch("app.services.userService.loadUsers")
def test_getUserByIdNotFound(mockLoad):
    mockLoad.return_value = []
    with pytest.raises(userService.UserNotFoundError):
        userService.getUserById(999)


# this tests that a current user is updated and saved correctly according to our schema
@patch("app.services.userService.saveUsers")
@patch("app.services.userService.loadUsers")
def test_updateUserSuccess(mockLoad, mockSave, fakeUsers):
    mockLoad.return_value = fakeUsers

    payload = UserUpdate(
        firstName="Updated",
        lastName="Name",
        age=28,
        email="updated@example.com",
        username="updateduser",
        pw="NewP@ssw0rd",
    )

    assert fakeUsers[0].username != "updateduser"
    updated = userService.updateUser(1, payload)
    assert updated.firstName == "Updated"
    assert updated.username == "updateduser"
    mockSave.assert_called_once()


# this tests that an error is raised when trying to update a user that does not exist
@patch("app.services.userService.saveUsers")
@patch("app.services.userService.loadUsers")
def test_updateUserNotFound(mockLoad, mockSave):
    mockLoad.return_value = []
    payload = UserUpdate(
        firstName="Missing",
        lastName="Person",
        age=40,
        email="missing@example.com",
        username="missing",
        pw="NewP@ssw0rd",
    )

    with pytest.raises(userService.UserNotFoundError):
        userService.updateUser(999, payload)


# this tests that a user is deleted correctly
@patch("app.services.userService.saveUsers")
@patch("app.services.userService.loadUsers")
def test_deleteUserSuccess(mockLoad, mockSave, fakeUsers):
    mockLoad.return_value = fakeUsers
    userService.deleteUser(1)
    mockSave.assert_called_once()


# this tests that an error is raised when trying to delete a user that does not exist
@patch("app.services.userService.saveUsers")
@patch("app.services.userService.loadUsers")
def test_deleteUserNotFound(mockLoad, mockSave, fakeUsers):
    mockLoad.return_value = fakeUsers
    with pytest.raises(userService.UserNotFoundError):
        userService.deleteUser(999)
