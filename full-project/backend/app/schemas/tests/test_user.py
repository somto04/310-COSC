import pytest
from pydantic import ValidationError
from ..user import User, UserCreate, UserUpdate
from ..role import Role


def test_user_valid_input():
    user = User(
        id=1,
        username="testuser",
        firstName="Test",
        lastName="User",
        age=20,
        email="test@example.com",
        pw="HashedPw123",
        role=Role.USER,
        penalties=0,
        isBanned=False,
    )
    assert user.username == "testuser"
    assert user.age == 20
    assert user.role == Role.USER


def test_user_invalid_email():
    with pytest.raises(ValidationError):
        UserCreate(
            firstName="Bob",
            lastName="Smith",
            age=20,
            email="not-an-email",
            username="bobsmith",
            pw="Password123",
        )


def test_usercreate_invalid_age():
    with pytest.raises(ValidationError):
        UserCreate(
            firstName="Bob",
            lastName="Smith",
            age=15,  # too young
            email="bob@example.com",
            username="bobsmith",
            pw="Password123",
        )


def test_username_constraints():
    with pytest.raises(ValidationError):
        UserCreate(
            firstName="Test",
            lastName="User",
            age=20,
            email="x@example.com",
            username="ab",  # too short
            pw="Password123",
        )

    with pytest.raises(ValidationError):
        UserCreate(
            firstName="Test",
            lastName="User",
            age=20,
            email="x@example.com",
            username="bad space",  # invalid pattern
            pw="Password123",
        )

    good = UserCreate(
        firstName="Ok",
        lastName="User",
        age=20,
        email="ok@example.com",
        username="valid_name-123",
        pw="Password123",
    )
    assert good.username == "valid_name-123"


def test_password_constraints():
    with pytest.raises(ValidationError):
        UserCreate(
            firstName="Bad",
            lastName="Pass",
            age=20,
            email="bad@example.com",
            username="validuser",
            pw="short",  # too short
        )

    ok = UserCreate(
        firstName="Good",
        lastName="Pass",
        age=20,
        email="good@example.com",
        username="user123",
        pw="Longenough123",
    )
    assert ok.pw == "Longenough123"


def test_userupdate_partial_update():
    base = User(
        id=1,
        username="olduser",
        firstName="Old",
        lastName="Name",
        age=30,
        email="old@example.com",
        pw="oldhashedpW123",
        role=Role.USER,
        penalties=0,
        isBanned=False,
    )

    update_data = UserUpdate(
        firstName="NewFirst", email="new@example.com"
    )  # type: ignore[call-arg]

    update_dict = update_data.model_dump(exclude_unset=True)
    updated = base.model_copy(update=update_dict)

    assert updated.firstName == "NewFirst"
    assert updated.email == "new@example.com"

    # unchanged
    assert updated.lastName == "Name"
    assert updated.username == "olduser"
    assert updated.role == Role.USER
    assert updated.isBanned is False


def test_userupdate_invalid_age():
    with pytest.raises(ValidationError):
        UserUpdate(
            age=15  # too young
        )  # type: ignore[call-arg]


def test_userupdate_password_constraints():
    with pytest.raises(ValidationError):
        UserUpdate(
            pw="nopass"  # too short / no complexity
        )  # type: ignore[call-arg]

    ok = UserUpdate(pw="NewStrongPw1")  # type: ignore[call-arg]

    assert ok.pw == "NewStrongPw1"
