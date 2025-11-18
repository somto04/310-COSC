from typing import List, Dict, Any
from .repo import _base_load_all, _base_save_all, DATA_DIR
from ..schemas.user import User

USER_DATA_FILE = DATA_DIR / "users.json"

def loadAll() -> List[User]:
    """
    Load all users from the users data file.

    Returns:
        List[User]: A list of users.
    """

    user_dicts = _base_load_all(USER_DATA_FILE)
    return [User(**user) for user in user_dicts]

def saveAll(items: List[Dict[str, Any]]) -> None:
    """
    Save all users to the users data file.

    Args:
        items (List[Dict[str, Any]]): A list of user items to save.
    """
    _base_save_all(USER_DATA_FILE, items)

__all__ = ["loadAll", "saveAll"]