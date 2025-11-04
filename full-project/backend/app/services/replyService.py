from datetime import datetime
from fastapi import HTTPException
from ..schemas.review import Reply, ReplyCreate
from ..repos.replyRepo import loadAll, saveAll

# lists all replies for a given review
def list_replies(reviewId: int):
    replies = loadAll()
    return [Reply(**reply) for reply in replies if reply["reviewId"] == reviewId]

# creates a new reply
def create_reply(payload: ReplyCreate) -> Reply:
    replies = loadAll()

    # generate a new unique integer ID (auto-increment)
    if replies:
        newId = max([int(r.get("id", 0)) for r in replies]) + 1
    else:
        newId = 1

    new_reply = Reply(
        id=newId,
        reviewId=payload.reviewId,
        userId=payload.userId,
        replyBody=payload.replyBody.strip() if payload.replyBody else "",
        # date posted is optional, if not provided use current date
        datePosted=payload.datePosted or datetime.now().strftime("%d %B %Y")
    )

    # append the new reply and save
    replies.append(new_reply.model_dump())
    saveAll(replies)
    return new_reply
