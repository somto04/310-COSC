from pydantic import BaseModel
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
    age: int
    email: str
    username: str
    pw: str
    role: str

class UserUpdate(BaseModel):
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    age: Optional[int] = None
    email: Optional[str] = None
    username: Optional[str] = None
    pw: Optional[str] = None
    role: Optional[str] = None
