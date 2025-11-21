from typing import List
from .repo import baseLoadAll, baseSaveAll, DATA_DIR
from ..schemas.user import User

_USER_DATA_PATH = DATA_DIR / "users.json"
_USER_CACHE: List[User] | None = None
_NEXT_USER_ID: int | None = None


def getMaxUserId(users: List[User]) -> int:
    """
    Return the maximum user ID in a list of users, or 0 if empty.
    """
    return max((user.id for user in users), default=0)


def loadCache() -> List[User]:
    """
    Load users from the data file into a cache.

    Loads the users only once and caches them for future calls.
    Also initializes the next user ID.
    Returns:
        List[User]: A list of users.
    """
    global _USER_CACHE, _NEXT_USER_ID
    if _USER_CACHE is None:
        user_dicts = baseLoadAll(_USER_DATA_PATH)
        _USER_CACHE = [User(**user) for user in user_dicts]

        max_id = getMaxUserId(_USER_CACHE)
        _NEXT_USER_ID = max_id + 1
    return _USER_CACHE


def getNextUserId() -> int:
    """
    Get the next available user ID.

    Returns:
        int: The next user ID.
    """
    global _NEXT_USER_ID
    if _NEXT_USER_ID is None:
        loadCache()

    assert _NEXT_USER_ID is not None

    next_id = _NEXT_USER_ID
    _NEXT_USER_ID += 1
    return next_id


def loadUsers() -> List[User]:
    """
    Load all users from the users data file.

    Returns:
        List[User]: A list of users.
    """
    return loadCache()


def saveUsers(users: List[User]):
    """
    Save all users to the users data file.

    Args:
        users (List[User]): A list of users to save.
    """
    global _USER_CACHE, _NEXT_USER_ID
    _USER_CACHE = users

    max_id = getMaxUserId(users)
    if _NEXT_USER_ID is None or _NEXT_USER_ID <= max_id:
        _NEXT_USER_ID = max_id + 1

    user_dicts = [user.model_dump() for user in users]
    baseSaveAll(_USER_DATA_PATH, user_dicts)


__all__ = ["loadUsers", "saveUsers"]
