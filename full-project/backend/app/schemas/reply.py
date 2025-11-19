from pydantic import BaseModel
from typing import Optional

class Reply(BaseModel):
    id: int
    # this refers to the review the reply is associated with
    reviewId: int
    userId: int
    replyBody: str
    datePosted: str

class ReplyCreate(BaseModel):
    reviewId: int
    userId: int
    replyBody: str
    datePosted: str
