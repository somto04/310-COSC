from fastapi import APIRouter, Depends
from typing import List
from ..schemas.review import Reply, ReplyCreate
from ..services.replyService import list_replies, create_reply
from .auth import getCurrentUser

router = APIRouter(prefix="/replies", tags=["replies"])

# Endpoint to get all replies for a specific review
@router.get("/{reviewId}", response_model=List[Reply])
def getReplies(reviewId: str):
    return list_replies(reviewId)

# Endpoint to create a new reply
@router.post("", response_model=Reply)
#def postReply(payload: ReplyCreate, currentUser: dict = Depends(getCurrentUser)):
def postReply(payload: ReplyCreate):
    return create_reply(payload)
