from datetime import datetime
from ..schemas.review import Reply, ReplyCreate
from ..repos.replyRepo import loadAll, saveAll

def list_replies(reviewId: int):
    replies = loadAll()
    return [Reply(**reply) for reply in replies if reply["reviewId"] == reviewId]

def create_reply(payload: ReplyCreate) -> Reply:
    """ Creates a new reply and adds to json """
    replies = loadAll()

    if replies:
        newId = max([int(r.get("id", 0)) for r in replies]) + 1
    else:
        newId = 1

    new_reply = Reply(
        id=newId,
        reviewId=payload.reviewId,
        userId=payload.userId,
        replyBody=payload.replyBody.strip() if payload.replyBody else "",
        datePosted=payload.datePosted or datetime.now().strftime("%d %B %Y")
    )

    replies.append(new_reply.model_dump())
    saveAll(replies)
    return new_reply
