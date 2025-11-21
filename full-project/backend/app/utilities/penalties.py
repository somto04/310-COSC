from typing import Optional
from ..repos.userRepo import loadUsers, saveUsers
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
    Increase penaltyCount for a user and ban them if max reached.
    Returns the updated User model.
    """
    users = loadUsers()
    updatedUser = None

    # loop with index so we can update the list
    for i, user in enumerate(users):
        if int(user.id) == int(userId):
            user.penalties += 1

            if user.penalties >= MAX_PENALTIES:
                user.isBanned = True

            updatedUser = user
            users[i] = user 
            break

    if updatedUser is None:
        raise ValueError("User not found")

    saveUsers(users)
    return updatedUser




