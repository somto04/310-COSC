from pydantic import (
    BaseModel,
    Field,
    field_validator,
    StringConstraints,
    AliasChoices,
)
from typing import Annotated, Optional
from .role import Role
import re

MAX_NAME_LENGTH = 50
MIN_EMAIL_LENGTH = 5
MAX_EMAIL_LENGTH = 254
MIN_AGE = 16
MAX_AGE = 120
PASSWORD_RE = re.compile(r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d).+$")
MIN_USERNAME_LENGTH = 3
MAX_USERNAME_LENGTH = 30
MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 128

Username = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=MIN_USERNAME_LENGTH,
        max_length=MAX_USERNAME_LENGTH,
        pattern=r"^[A-Za-z0-9_.-]+$",
    ),
]
Password = Annotated[
    str,
    StringConstraints(
        min_length=MIN_PASSWORD_LENGTH,
        max_length=MAX_PASSWORD_LENGTH,
    ),
]
Email = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=MIN_EMAIL_LENGTH,
        max_length=MAX_EMAIL_LENGTH,
        pattern=r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$",
    ),
]


class User(BaseModel):
    """
    Schema representing a user in the system.

    Attributes:
        id (int): Unique identifier for the user.
        username (Username): Unique username following defined constraints.
        firstName (str): User's first name.
        lastName (str): User's last name.
        age (Optional[int]): User's age.
        email (Email): User's validated email address.
        pw (Password): Hashed password.
        role (Role): Role of the user in the system.
        penalties (int): Number of penalties assigned to the user.
        isBanned (bool): Indicates if the user is banned.
    """

    id: int
    username: str
    firstName: str = ""
    lastName: str = ""
    age: Optional[int] = None
    email: Email = ""
    pw: str
    role: Role = Role.USER
    penalties: int = Field(
        default=0, validation_alias=AliasChoices("penaltyCount", "penalties")
    )
    isBanned: bool = False


class UserCreate(BaseModel):
    """
    Schema for creating a new user.

    Only exposes necessary fields for user creation.

    Attributes:
        username (Username): Unique username following defined constraints.
        firstName (str): User's first name.
        lastName (str): User's last name.
        age (int): User's age.
        email (Email): User's validated email address.
        pw (Password): Password following defined constraints.
    """

    username: Username = Field(..., description="Unique username for the user")
    firstName: str = Field(
        ..., min_length=1, max_length=MAX_NAME_LENGTH, description="User's first name"
    )
    lastName: str = Field(
        ..., min_length=1, max_length=MAX_NAME_LENGTH, description="User's last name"
    )
    age: int = Field(
        ...,
        ge=MIN_AGE,
        le=MAX_AGE,
        description=f"User must be {MIN_AGE} years or older",
    )
    email: Email = Field(..., description="User's email address")
    pw: Password = Field(..., description="Password for the user account")

    @field_validator("age")
    @classmethod
    def check_age(cls, user_age):
        if user_age < MIN_AGE:
            raise ValueError(
                f"User must be {MIN_AGE} years or older to create an account"
            )
        return user_age

    @field_validator("pw")
    @classmethod
    def password_complexity(cls, pw: str):
        if not PASSWORD_RE.match(pw):
            raise ValueError("Password must contain uppercase, lowercase, and a digit")
        return pw


class UserUpdate(BaseModel):
    """
    Schema for updating user information.

    All fields are optional to allow partial updates.

    Attributes:
        username (Optional[Username]): Unique username for the user.
        firstName (Optional[str]): User's first name.
        lastName (Optional[str]): User's last name.
        age (Optional[int]): User's age.
        email (Optional[Email]): User's email address.
        pw (Optional[Password]): Password for the user account.
    """

    username: Optional[Username] = None
    firstName: Optional[str] = Field(None, min_length=1, max_length=MAX_NAME_LENGTH)
    lastName: Optional[str] = Field(None, min_length=1, max_length=MAX_NAME_LENGTH)
    age: Optional[int] = Field(None, ge=MIN_AGE, le=MAX_AGE)
    email: Optional[Email] = None
    pw: Optional[Password] = None

    @field_validator("age")
    @classmethod
    def check_age(cls, user_age):
        if user_age is not None and user_age < MIN_AGE:
            raise ValueError(
                f"User must be {MIN_AGE} years or older to update an account"
            )
        return user_age

    @field_validator("pw")
    @classmethod
    def password_complexity(cls, pw: str):
        if not PASSWORD_RE.match(pw):
            raise ValueError("Password must contain uppercase, lowercase, and a digit")
        return pw


class AdminUserUpdate(UserUpdate):
    """
    Schema for updating user information by an admin.

    Inherits from UserUpdate and allows modification of all fields, including role, penalties, and ban status.
    Only exposes fields that an admin can update.

    Attributes:
        ... from UserUpdate
        role (Optional[Role]): Role of the user in the system.
        penalties (Optional[int]): Number of penalties assigned to the user.
        isBanned (Optional[bool]): Indicates if the user is banned.
    """

    role: Optional[Role] = None
    penalties: Optional[int] = Field(
        None, validation_alias=AliasChoices("penaltyCount", "penalties")
    )
    isBanned: Optional[bool] = None


class CurrentUser(BaseModel):
    """
    Schema representing the currently authenticated user.

    Only exposes non-sensitive information.

    Attributes:
        id (int): Unique identifier for the user.
        username (Username): Unique username following defined constraints.
        role (Role): Role of the user in the system.
    """

    id: int
    username: Username
    role: Role
