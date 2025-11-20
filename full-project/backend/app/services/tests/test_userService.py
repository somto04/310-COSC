import pytest
import uuid
from fastapi import HTTPException
from unittest.mock import patch
from app.services import userService
from app.schemas.user import User, UserCreate, UserUpdate


#these fixtures provide mock user data for testing that follows our user schema
@pytest.fixture
def fake_users():
    return [
        {
            "id": 1,
            "firstName": "Alex",
            "lastName": "Mason",
            "age": 25,
            "email": "alex@example.com",
            "username": "alexm",
            "pw": "hashed_pw_1",
            "role": "admin",
        },
        {
            "id": 2,
            "firstName": "Jade",
            "lastName": "Taylor",
            "age": 30,
            "email": "jade@example.com",
            "username": "jadet",
            "pw": "hashed_pw_2",
            "role": "user",
        },
    ]



#this tests that all users currently stored are listed correctly
@patch("app.services.userService.loadAll")
def test_list_users(mock_load, fake_users):
    mock_load.return_value = fake_users
    result = userService.listUsers()
    assert len(result) == 2
    assert all(isinstance(u, User) for u in result)

#this tests that a new user is created and saved correctly according to our schema
@patch("app.services.userService.saveAll")
@patch("app.services.userService.loadAll")
def test_create_user(mock_load, mock_save, fake_users):
    mock_load.return_value = fake_users

    payload = UserCreate(
        firstName="Sam",
        lastName="Hill",
        age=22,
        email="sam@example.com",
        username="samh",
        pw="pass12345678",
        role="user",
    )

    new_user = userService.createUser(payload)
    assert new_user.firstName == "Sam"
    assert new_user.username == "samh"
    mock_save.assert_called_once()

#this tests that a user can be retrieved by their ID correctly
@patch("app.services.userService.loadAll")
def test_get_user_by_id_found(mock_load, fake_users):
    mock_load.return_value = fake_users
    result = userService.getUserById(1)
    assert result.username == "alexm"

#this tests that an error is raised when trying to get a user that does not exist
@patch("app.services.userService.loadAll")
def test_get_user_by_id_not_found(mock_load):
    mock_load.return_value = []
    with pytest.raises(HTTPException) as exc:
        userService.getUserById(999)
    assert exc.value.status_code == 404

# this tests that a current user is updated and saved correctly according to our schema
@patch("app.services.userService.saveAll")
@patch("app.services.userService.loadAll")
def test_update_user_success(mock_load, mock_save, fake_users):
    mock_load.return_value = fake_users

    payload = UserUpdate(
        firstName="Updated",
        lastName="Name",
        age=28,
        email="updated@example.com",
        username="updateduser",
        pw="newpw1245678",
        role="admin",
    )

    updated = userService.updateUser(1, payload)
    assert updated.firstName == "Updated"
    assert updated.role == "admin"
    mock_save.assert_called_once()

# this tests that an error is raised when trying to update a user that does not exist
@patch("app.services.userService.saveAll")
@patch("app.services.userService.loadAll")
def test_update_user_not_found(mock_load, mock_save):
    mock_load.return_value = []
    payload = UserUpdate(
        firstName="Missing",
        lastName="Person",
        age=40,
        email="missing@example.com",
        username="missing",
        pw="123456789",
        role="user",
    )

    with pytest.raises(HTTPException) as exc:
        userService.updateUser(999, payload)
    assert exc.value.status_code == 404

# this tests that a user is deleted correctly
@patch("app.services.userService.saveAll")
@patch("app.services.userService.loadAll")
def test_delete_user_success(mock_load, mock_save, fake_users):
    mock_load.return_value = fake_users
    userService.deleteUser(1)
    mock_save.assert_called_once()

# this tests that an error is raised when trying to delete a user that does not exist
@patch("app.services.userService.saveAll")
@patch("app.services.userService.loadAll")
def test_delete_user_not_found(mock_load, mock_save, fake_users):
    mock_load.return_value = fake_users
    with pytest.raises(HTTPException) as exc:
        userService.deleteUser(999)
    assert exc.value.status_code == 404
