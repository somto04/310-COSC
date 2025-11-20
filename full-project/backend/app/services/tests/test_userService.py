import pytest
import uuid
from fastapi import HTTPException
from unittest.mock import patch
from app.services import userService
from app.schemas.user import User, UserCreate, UserUpdate
from app.schemas.role import Role
from app.utilities.security import verifyPassword


# these fixtures provide mock user data for testing that follows our user schema
@pytest.fixture
def fake_users():
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
def test_list_users(mock_load, fake_users):
    mock_load.return_value = fake_users
    result = userService.listUsers()
    assert len(result) == 2
    assert all(isinstance(u, User) for u in result)


# this tests that a new user is created and saved correctly according to our schema
@patch("app.services.userService.saveUsers")
@patch("app.services.userService.loadUsers")
def test_create_user(mock_load, mock_save, fake_users):
    mock_load.return_value = list(fake_users)

    payload = UserCreate(
        firstName="Sam",
        lastName="Hill",
        age=22,
        email="sam@example.com",
        username="samh",
        pw="SecureP@ss123",
    )

    new_user = userService.createUser(payload)
    assert new_user.firstName == "Sam"
    assert new_user.username == "samh"
    assert new_user.id == 3
    assert new_user.pw != payload.pw
    assert new_user.pw.startswith("$2")
    mock_save.assert_called_once()

    args, kwargs = mock_save.call_args
    saved_users = args[0]

    assert len(saved_users) == 3 
    assert saved_users[-1] == new_user
    assert isinstance(saved_users[-1], User)


@patch("app.services.userService.saveUsers")
@patch("app.services.userService.loadUsers")
def test_create_user_hashes_password(mock_load, mock_save, fake_users):
    mock_load.return_value = fake_users

    plain_pw = "Pass123A"
    payload = UserCreate(
        username="newuser",
        firstName="Sam",
        lastName="Hill",
        age=22,
        email="sam@example.com",
        pw=plain_pw,
    )

    new_user = userService.createUser(payload)

    # 1. Should not store raw password
    assert new_user.pw != plain_pw

    # 2. Hash should actually verify
    assert verifyPassword(plain_pw, new_user.pw)

    # 3. Still only one save
    mock_save.assert_called_once()

    # 4. check what got saved
    saved_users = mock_save.call_args[0][0]
    assert saved_users[-1].pw == new_user.pw


@patch("app.services.userService.loadUsers")
def test_create_user_username_taken(mock_load, fake_users):
    mock_load.return_value = fake_users

    payload = UserCreate(
        firstName="Alex",
        lastName="Mason",
        age=25,
        email="alex@example.com",
        username="alexm",
        pw="SomePassword123",
    )

    with pytest.raises(HTTPException) as exc:
        userService.createUser(payload)
    assert exc.value.status_code == 409


# this tests that a user can be retrieved by their ID correctly
@patch("app.services.userService.loadUsers")
def test_get_user_by_id_found(mock_load, fake_users):
    mock_load.return_value = fake_users
    result = userService.getUserById(1)
    assert result.username == "alexm"


# this tests that an error is raised when trying to get a user that does not exist
@patch("app.services.userService.loadUsers")
def test_get_user_by_id_not_found(mock_load):
    mock_load.return_value = []
    with pytest.raises(HTTPException) as exc:
        userService.getUserById(999)
    assert exc.value.status_code == 404


# this tests that a current user is updated and saved correctly according to our schema
@patch("app.services.userService.saveUsers")
@patch("app.services.userService.loadUsers")
def test_update_user_success(mock_load, mock_save, fake_users):
    mock_load.return_value = fake_users

    payload = UserUpdate(
        firstName="Updated",
        lastName="Name",
        age=28,
        email="updated@example.com",
        username="updateduser",
        pw="NewP@ssw0rd",
    )

    assert fake_users[0].username != "updateduser"
    updated = userService.updateUser(1, payload)
    assert updated.firstName == "Updated"
    assert updated.username == "updateduser"
    mock_save.assert_called_once()


# this tests that an error is raised when trying to update a user that does not exist
@patch("app.services.userService.saveUsers")
@patch("app.services.userService.loadUsers")
def test_update_user_not_found(mock_load, mock_save):
    mock_load.return_value = []
    payload = UserUpdate(
        firstName="Missing",
        lastName="Person",
        age=40,
        email="missing@example.com",
        username="missing",
        pw="NewP@ssw0rd",
    )

    with pytest.raises(HTTPException) as exc:
        userService.updateUser(999, payload)
    assert exc.value.status_code == 404


# this tests that a user is deleted correctly
@patch("app.services.userService.saveUsers")
@patch("app.services.userService.loadUsers")
def test_delete_user_success(mock_load, mock_save, fake_users):
    mock_load.return_value = fake_users
    userService.deleteUser(1)
    mock_save.assert_called_once()


# this tests that an error is raised when trying to delete a user that does not exist
@patch("app.services.userService.saveUsers")
@patch("app.services.userService.loadUsers")
def test_delete_user_not_found(mock_load, mock_save, fake_users):
    mock_load.return_value = fake_users
    with pytest.raises(HTTPException) as exc:
        userService.deleteUser(999)
    assert exc.value.status_code == 404
