from typing import List
from.repo import _baseSaveAll, _baseLoadAll, DATA_DIR
from ..schemas.reply import Reply

_REPLY_DATA_PATH = DATA_DIR / "replies.json"
_REPLY_CACHE: List[Reply] | None = None
_NEXT_REPLY_ID: int | None = None

def getMaxReplyId(replies: List[Reply]) -> int:
    """
    Return the maximum reply ID in a list of replies, or 0 if empty.
    """
    return max((reply.id for reply in replies), default=0)


def _loadReplyCache() -> List[Reply]: 
    """
    Load reply from the data file into a cache.

    Loads the reply only once and caches them for future calls.
    Returns:
        List[Reply]: A list of reply.
    """
    global _REPLY_CACHE, _NEXT_REPLY_ID
    if _REPLY_CACHE is None:
        reply_dicts = _baseLoadAll(_REPLY_DATA_PATH)
        _REPLY_CACHE = [Reply(**reply) for reply in reply_dicts]
        _NEXT_REPLY_ID = getMaxReplyId(_REPLY_CACHE) + 1
    return _REPLY_CACHE

def getNextReplyId() -> int:
    """
    Get the next available reply ID.

    Returns:
        int: The next reply ID.
    """
    global _NEXT_REPLY_ID
    if _NEXT_REPLY_ID is None:
        _loadReplyCache()

    assert _NEXT_REPLY_ID is not None

    next_id = _NEXT_REPLY_ID
    _NEXT_REPLY_ID += 1
    return next_id

def loadReplies() -> List[Reply]: 
    """
    Load all replies from the replies data file.

    Returns:
        List[Reply]: A list of reply items.
    """
    return _loadReplyCache()
    
def saveReplies(replies: List[Reply]) -> None: 
    """
    Save all replies to the reviews data file.

    Args:
        replies (List[Reply]): A list of reply items to save.
    """
    global _REPLY_CACHE
    _REPLY_CACHE = replies
    reply_dict = [reply.model_dump() for reply in replies]
    _baseSaveAll(_REPLY_DATA_PATH, reply_dict)

__all__ = ["loadReplies", "saveReplies", "getNextReplyId"]
