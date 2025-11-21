from pydantic import BaseModel
from typing import Optional

class Reply(BaseModel):
    id: int
    reviewId: int
    userId: int
    replyBody: str
    datePosted: str

class ReplyCreate(BaseModel):
    reviewId: int
    userId: int
    replyBody: str
    datePosted: str
