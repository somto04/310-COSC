from pydantic import BaseModel, Field, field_validator, EmailStr, StringConstraints
from typing import Annotated, Optional
from .role import Role

MAX_NAME_LENGTH = 50
MAX_EMAIL_LENGTH = 254
MIN_AGE = 16
MAX_AGE = 120

Username = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=3,
        max_length=30,
        pattern=r"^[A-Za-z0-9_.-]+$",
    ),
]

Password = Annotated[
    str,
    StringConstraints(
        min_length=8,
        max_length=128,
        pattern=r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d).+$"
    ),
]


class User(BaseModel):
    """
    Schema representing a user in the system.
    """

    id: int
    username: str
    firstName: str = ""
    lastName: str = ""
    age: Optional[int] = None
    email: EmailStr = ""
    pw: str
    role: Role
    penalties: int = Field(0, alias="penaltyCount")
    isBanned: bool = False


class UserCreate(BaseModel):
    """
    Schema for creating a new user.

    Only exposes necessary fields for user creation.
    """

    firstName: str = Field(
        ..., min_length=1, max_length=MAX_NAME_LENGTH, description="User's first name"
    )
    lastName: str = Field(
        ..., min_length=1, max_length=MAX_NAME_LENGTH, description="User's last name"
    )
    age: int = Field(
        ..., ge=MIN_AGE, le=MAX_AGE, description="User must be 16 years or older"
    )
    email: EmailStr = Field(
        ..., max_length=MAX_EMAIL_LENGTH, description="User's email address"
    )
    username: Username = Field(..., description="Unique username for the user")
    pw: Password = Field(..., description="Password for the user account")

    @field_validator("age")
    @classmethod
    def check_age(cls, user_age):
        if user_age < 16:
            raise ValueError("User must be 16 years or older to create an account")
        return user_age


class UserUpdate(BaseModel):
    """
    Schema for updating user information.

    All fields are optional to allow partial updates.
    """

    firstName: Optional[str] = Field(None, min_length=1, max_length=MAX_NAME_LENGTH)
    lastName: Optional[str] = Field(None, min_length=1, max_length=MAX_NAME_LENGTH)
    age: Optional[int] = Field(None, ge=MIN_AGE, le=MAX_AGE)
    email: Optional[EmailStr] = Field(None, max_length=MAX_EMAIL_LENGTH)
    username: Optional[Username] = None
    pw: Optional[Password] = None

    @field_validator("age")
    @classmethod
    def check_age(cls, user_age):
        if user_age is not None and user_age < 16:
            raise ValueError("User must be 16 years or older to update an account")
        return user_age


class AdminUserUpdate(UserUpdate):
    """
    Schema for updating user information by an admin.

    Inherits from UserUpdate and allows modification of all fields, including role, penalties, and ban status.
    """

    role: Optional[Role] = None
    penalties: Optional[int] = None
    isBanned: Optional[bool] = None


class CurrentUser(BaseModel):
    """
    Schema representing the currently authenticated user.

    Only exposes non-sensitive information.
    """

    id: int
    username: str
    role: Role
