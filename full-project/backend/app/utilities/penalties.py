from typing import Optional
from ..repos.userRepo import loadAll as loadUsers, saveAll as saveUsers
from ..schemas.user import User

MAX_PENALTIES = 3  # how many strikes before ban

def findUserByUsername(username: str) -> Optional[User]:
    users = loadUsers()
    for user in users:
        if user.username == username:
            return user
    return None

def incrementPenaltyForUser(userId: int) -> User:
    """
    Increase penaltyCount for a user and ban if max reached.
    
    Returns:
        The updated user with penalties applied if needed.
        
    Raises: 
        ValueError: if the user isnt found.
    """
    users = loadUsers()
    updatedUser = None

    from typing import Optional
from ..repos.userRepo import loadAll as loadUsers, saveAll as saveUsers  # adjust path

MAX_PENALTIES = 3  # how many strikes before ban

def findUserByUsername(username: str) -> Optional[dict]:
    users = loadUsers()
    for u in users:
        if u.get("username") == username:
            return u
    return None

def incrementPenaltyForUser(userId: int) -> dict:
    """
    Increase penaltyCount for a user and ban if max reached.
    
    Returns:
        The updated user with penalties applied if needed.
        
    Raises: 
        ValueError: if the user isnt found.
    """
    users = loadUsers()
    updatedUser = None
   
    for i, user in enumerate(users):
        if int(user.id) == int(userId):
            user.penaltyCount += 1

            if user.penaltyCount >= MAX_PENALTIES:
                user.isBanned = True

            updated_user = user
            users[i] = user
            break

    if updated_user is None:
        raise ValueError("User not found")

    saveUsers(users)
    return updated_user

def setUserBanned(userId: int, isBanned: bool) -> User:
    users = loadUsers()

    for i, user in enumerate(users):
        if int(user.id) == int(userId):
            user.isBanned = bool(isBanned)
            users[i] = user
            saveUsers(users)
            return user

    raise ValueError("User not found")