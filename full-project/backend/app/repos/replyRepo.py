from typing import List
from.repo import _base_save_all, _base_load_all
from ..schemas.reply import Reply

REPLY_DATA_PATH = "app/data/replies.json"
_REPLY_CACHE: List[Reply] | None = None

def _load_reply_cache() -> List[Reply]: 
    """
    Load reply from the data file into a cache.

    Loads the reply only once and caches them for future calls.
    Returns:
        List[Reply]: A list of reply.
    """
    global _REPLY_CACHE
    if _REPLY_CACHE is None:
        reply_dicts = _base_load_all(_REPLY_CACHE)
        _REPLY_CACHE = [Reply(**reply) for reply in reply_dicts]
    return _REPLY_CACHE

def loadReplies() -> List[Reply]: 
    """
    Load all replies from the replies data file.

    Returns:
        List[Reply]: A list of reply items.
    """
    return _load_reply_cache
    
def saveReplies(replies: List[Reply]) -> None: 
    """
    Save all replies to the reviews data file.

    Args:
        replies (List[Reply]): A list of reply items to save.
    """
    global _REPLY_CACHE
    _REPLY_CACHE = replies
    reply_dict = [reply.model_dump() for reply in replies]
    _base_save_all(REPLY_DATA_PATH, reply_dict)

__all__ = ["loadAll", "saveAll"]
