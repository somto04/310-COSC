from typing import List, Dict, Any
from .repo import _base_load_all, _base_save_all, DATA_DIR
from ..schemas.user import User

_USER_DATA_PATH = DATA_DIR / "users.json"
_USER_CACHE: List[User] | None = None

def _load_cache() -> List[User]:
    """
    Load users from the data file into a cache.

    Helper to load users efficiently.
    Returns:
        List[User]: A list of users.
    """
    global _USER_CACHE
    if _USER_CACHE is None:
        user_dicts = _base_load_all(_USER_DATA_PATH)
        _USER_CACHE = [User(**user) for user in user_dicts]
    return _USER_CACHE

def loadAll() -> List[User]:
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
    user_dicts = [user.model_dump() for user in users]
    _base_save_all(_USER_DATA_PATH, user_dicts)


__all__ = ["loadAll", "saveAll"]
