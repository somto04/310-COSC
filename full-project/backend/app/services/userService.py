import uuid
from typing import List
from fastapi import HTTPException
from ..schemas.user import User, UserCreate, UserUpdate
from ..repos.userRepo import loadAll, saveAll

def listUsers() -> List[User]:
    return [User(**it) for it in loadAll()]

def createUser(payload: UserCreate) -> User:
    users = loadAll()
    uniqueUsername = payload.username.strip()
    newId = max([int(u["id"]) for u in users], default=0) + 1

    if any(int(it.get("id")) == newId for it in users):
        raise HTTPException(status_code=409, detail="ID collision; retry.")
    
    # converts both usernames to lowercase before comparing to ensure that its case insensitive
    # makes sure that the new username is unique
    if any(it.get("username", "").strip().lower() == uniqueUsername.lower() for it in users):
        raise HTTPException(status_code=409, detail="username already taken; retry.")

    newUser = User(
        id=newId,
        firstName=payload.firstName.strip(),
        lastName=payload.lastName.strip(),
        age=payload.age,
        email=payload.email.strip(),
        username=uniqueUsername,
        pw=payload.pw.strip(),
        role=payload.role,
    )
    users.append(newUser.model_dump())
    saveAll(users)
    return newUser

def getUserById(userId: str) -> User:
    users = loadAll()
    for it in users:
        if str(it.get("id")) == str(userId):
            return User(**it)
    raise HTTPException(status_code=404, detail=f"User '{userId}' not found")

def updateUser(userId: str, payload: UserUpdate) -> User:
    users = loadAll()
    for idx, it in enumerate(users):
        if str(it.get("id")) == str(userId):
            current_user = User(**it)
            update_data = payload.model_dump(exclude_unset=True)
            
            # Create updated user by merging current data with update data
            updated_dict = current_user.model_dump()
            updated_dict.update(update_data)
            
            # Strip string fields if they're provided
            if 'firstName' in update_data and updated_dict['firstName']:
                updated_dict['firstName'] = updated_dict['firstName'].strip()
            if 'lastName' in update_data and updated_dict['lastName']:
                updated_dict['lastName'] = updated_dict['lastName'].strip()
            if 'email' in update_data and updated_dict['email']:
                updated_dict['email'] = updated_dict['email'].strip()
            if 'username' in update_data and updated_dict['username']:
                updated_dict['username'] = updated_dict['username'].strip()
            if 'pw' in update_data and updated_dict['pw']:
                updated_dict['pw'] = updated_dict['pw'].strip()
            
            updated = User(**updated_dict)
            users[idx] = updated.model_dump()
            saveAll(users)
            return updated
    raise HTTPException(status_code=404, detail=f"User '{userId}' not found")

def deleteUser(userId: str) -> None:
    users = loadAll()
    newUsers = [it for it in users if str(it.get("id")) != str(userId)]
    if len(newUsers) == len(users):
        raise HTTPException(status_code=404, detail=f"User '{userId}' not found")
    saveAll(newUsers)
