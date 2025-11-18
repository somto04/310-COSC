from pydantic import BaseModel, Field, field_validator, EmailStr
from typing import Optional
from .role import Role

class User(BaseModel):
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
    firstName: str
    lastName: str
    age: int = Field(..., ge=0, description="User must be 16 years or older")
    email: EmailStr
    username: str
    pw: str
    role: Role
    penalties: int = 0
    isBanned: bool = False

    @field_validator("age")
    @classmethod
    def check_age(cls, value):
        if value < 16:
            raise ValueError("User must be 16 years or older to create an account")
        return value


class UserUpdate(BaseModel):
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
    id: int
    username: str
    role: Role
