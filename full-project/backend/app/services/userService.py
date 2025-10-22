import uuid
from typing import List
from fastapi import HTTPException
from ..schemas.user import User, UserCreate, UserUpdate
from ..repos.userRepo import loadAll, saveAll

def listUsers() -> List[User]:
    return [User(**it) for it in loadAll()]

def createUser(payload: UserCreate) -> User:
    users = loadAll()
    newId = str(uuid.uuid4())
    if any(it.get("id") == newId for it in users):
        raise HTTPException(status_code=409, detail="ID collision; retry.")
    newUser = User(id=newId, 
                   firstname = payload.firstname.strip(), 
                   lastname = payload.lastname.strip(), 
                   age = payload.age.strip(),
                   email = payload.email.strip(),
                   username = payload.username.strip(),
                   pw = payload.pw.strip(),
                   role = payload.role)
    users.append(newUser.dict())
    saveAll(users)
    return newUser

def getUserById(userId: str) -> User:
    users = loadAll()
    for it in users:
        if it.get("id") == userId:
            return User(**it)
    raise HTTPException(status_code=404, detail=f"User '{userId}' not found")

def updateUser(userId: str, payload: UserUpdate) -> User:
    users = loadAll()
    for idx, it in enumerate(users):
        if it.get("id") == userId:
            updated = User(
                id=userId,
                firstname = payload.firstname.strip(), 
                lastname = payload.lastname.strip(), 
                age = payload.age.strip(),
                email = payload.email.strip(),
                username = payload.username.strip(),
                pw = payload.pw.strip(),
                role = payload.role,
            )
            users[idx] = updated.dict()
            saveAll(users)
            return updated
    raise HTTPException(status_code=404, detail=f"User '{userId}' not found")

def deleteUser(userId: str) -> None:
    users = loadAll()
    newUsers = [it for it in users if it.get("id") != userId]
    if len(newUsers) == len(users):
        raise HTTPException(status_code=404, detail=f"User '{userId}' not found")
    saveAll(newUsers)