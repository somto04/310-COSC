from fastapi import APIRouter, Depends
from typing import List
from ..schemas.reply import Reply, ReplyCreate
from ..services.replyService import list_replies, create_reply
from .auth import getCurrentUser
from ..schemas.user import CurrentUser

router = APIRouter(prefix="/replies", tags=["replies"])

@router.get("/{reviewId}", response_model=List[Reply])
def getReplies(reviewId: int):
    """ Returns all replies that match a reviewId """
    return list_replies(reviewId)

@router.post("", response_model=Reply)
def postReply(payload: ReplyCreate, currentUser: CurrentUser = Depends(getCurrentUser)):
    """ Creates a new reply (only logged in users are able to post one)"""
    return create_reply(payload)
