from typing import List
from .repo import _base_load_all, _base_save_all, DATA_DIR
from ..schemas.user import User

_USER_DATA_PATH = DATA_DIR / "users.json"
_USER_CACHE: List[User] | None = None
_NEXT_USER_ID: int | None = None


def _load_cache() -> List[User]:
    """
    Load users from the data file into a cache.

    Loads the users only once and caches them for future calls.
    Also initializes the next user ID.
    Returns:
        List[User]: A list of users.
    """
    global _USER_CACHE, _NEXT_USER_ID
    if _USER_CACHE is None:
        user_dicts = _base_load_all(_USER_DATA_PATH)
        _USER_CACHE = [User(**user) for user in user_dicts]

        max_id = max((user.id for user in _USER_CACHE), default=0)
        _NEXT_USER_ID = max_id + 1
    return _USER_CACHE


def get_next_user_id() -> int:
    """
    Get the next available user ID.

    Returns:
        int: The next user ID.
    """
    global _NEXT_USER_ID
    if _NEXT_USER_ID is None:
        _load_cache()

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
    return _load_cache()


def saveAll(users: List[User]):
    """
    Save all users to the users data file.

    Args:
        users (List[User]): A list of users to save.
    """
    global _USER_CACHE, _NEXT_USER_ID
    _USER_CACHE = users

    max_id = max((user.id for user in users), default=0)
    if _NEXT_USER_ID is None or _NEXT_USER_ID <= max_id:
        _NEXT_USER_ID = max_id + 1

    user_dicts = [user.model_dump() for user in users]
    _base_save_all(_USER_DATA_PATH, user_dicts)


__all__ = ["loadUsers", "saveAll"]
