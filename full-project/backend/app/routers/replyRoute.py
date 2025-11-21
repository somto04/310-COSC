from fastapi import APIRouter, Depends
from typing import List
from ..schemas.review import Reply, ReplyCreate
from ..services.replyService import listReplies, createReply
from .auth import getCurrentUser

router = APIRouter(prefix="/replies", tags=["replies"])

@router.get("/{reviewId}", response_model=List[Reply])
def getReplies(reviewId: int):
    """ Returns all replies that match a reviewId """
    return listReplies(reviewId)

@router.post("", response_model=Reply)
def postReply(payload: ReplyCreate, currentUser: dict = Depends(getCurrentUser)):
    """ Creates a mew reply (only logged in users are able to post one)"""
    return createReply(payload)
