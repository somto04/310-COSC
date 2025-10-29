from datetime import datetime
import uuid
from fastapi import HTTPException
from ..schemas.review import Reply, ReplyCreate
from ..repos.replyRepo import loadAll, saveAll

# lists all replies for a given review
def list_replies(reviewId: str):
    replies = loadAll()
    return [Reply(**reply) for reply in replies if reply["reviewId"] == reviewId]

# creates a new reply
def create_reply(payload: ReplyCreate) -> Reply:
    replies = loadAll()
    # no need to check for existing IDs since we generate a new one
    newId = str(uuid.uuid4())

    new_reply = Reply(
        id=newId,
        reviewId=payload.reviewId,
        userId=payload.userId,
        replyBody=payload.replyBody,
        #date posted is optional, if not provided use current date
        datePosted=payload.datePosted or datetime.now().strftime("%d %B %Y")
    )
    # append the new reply and save
    replies.append(new_reply.model_dump())
    saveAll(replies)
    return new_reply