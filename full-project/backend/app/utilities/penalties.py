from typing import Optional
from ..repos.userRepo import loadUsers as loadUsers, saveAll as saveUsers  # adjust path

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
    for u in users:
        if int(u.get("id")) == int(userId):
            u["penaltyCount"] = int(u.get("penaltyCount", 0)) + 1
            if u["penaltyCount"] >= MAX_PENALTIES:
                u["isBanned"] = True
            updatedUser = u
            break
    if updatedUser is None:
        raise ValueError("User not found")
    saveUsers(users)
    return updatedUser

def setUserBanned(userId: int, isBanned: bool):
    users = loadUsers()
    for u in users:
        if int(u.get("id")) == int(userId):
            u["isBanned"] = bool(isBanned)
            saveUsers(users)
            return u
    raise ValueError("User not found")
