from typing import List, Dict, Any
from .repo import _base_load_all, _base_save_all, DATA_DIR
from ..schemas.user import User

USER_DATA_PATH = DATA_DIR / "users.json"


def loadAll() -> List[User]:
    """
    Load all users from the users data file.

    Returns:
        List[User]: A list of users.
    """

    user_dicts = _base_load_all(USER_DATA_PATH)
    return [User(**user) for user in user_dicts]


def saveAll(users: List[User]):
    """
    Save all users to the users data file.

    Args:
        users (List[User]): A list of users to save.
    """
    user_dicts = [user.model_dump() for user in users]
    _base_save_all(USER_DATA_PATH, user_dicts)


__all__ = ["loadAll", "saveAll"]
