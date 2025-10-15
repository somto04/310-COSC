from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    userId: int
    firstname: str
    lastname: str
    age: int
    email: str
    username: str
    pw: str
    role: str

class UserCreate(BaseModel):
    firstname: str
    lastname: str
    age: int
    email: str
    username: str
    pw: str
    role: str

class UserUpdate(BaseModel):
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    age: Optional[int] = None
    email: Optional[str] = None
    username: Optional[str] = None
    pw: Optional[str] = None
    role: Optional[str] = None
