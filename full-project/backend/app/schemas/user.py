from pydantic import BaseModel, Field, field_validator
from typing import Optional

class User(BaseModel):
    id: int
    firstName: Optional[str] = ""
    lastName: Optional[str] = ""
    age: Optional[int] = None
    email: Optional[str] = ""
    username: str
    pw: Optional[str] = ""
    role: str

class UserCreate(BaseModel):
    firstName: str
    lastName: str
    age: int = Field(..., ge=0, description="User must be 16 years or older")
    email: str
    username: str
    pw: str
    role: str

    @field_validator('age')
    @classmethod
    def check_age(cls, value):
        if value < 16:
            raise ValueError("User must be 16 years or older to create an account")
        return value

class UserUpdate(BaseModel):
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    age: Optional[int] = None
    email: Optional[str] = None
    username: Optional[str] = None
    pw: Optional[str] = None
    role: Optional[str] = None

