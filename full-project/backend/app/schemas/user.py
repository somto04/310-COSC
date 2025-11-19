from pydantic import BaseModel, Field, field_validator, EmailStr
from typing import Optional
from .role import Role


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
    firstName: str
    lastName: str
    age: int = Field(..., ge=0, description="User must be 16 years or older")
    email: EmailStr
    username: str
    pw: str

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
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    age: Optional[int] = None
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    pw: Optional[str] = None
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
