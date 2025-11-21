from datetime import datetime
from ..schemas.review import Reply, ReplyCreate
from ..repos.replyRepo import loadAll, saveAll

def listReplies(reviewId: int):
    replies = loadAll()
    return [Reply(**reply) for reply in replies if reply["reviewId"] == reviewId]

def createReply(payload: ReplyCreate) -> Reply:
    """ Creates a new reply and adds to json """
    replies = loadAll()

    if replies:
        newId = max([int(r.get("id", 0)) for r in replies]) + 1
    else:
        newId = 1

    newReply = Reply(
        id=newId,
        reviewId=payload.reviewId,
        userId=payload.userId,
        replyBody=payload.replyBody.strip() if payload.replyBody else "",
        datePosted=payload.datePosted or datetime.now().strftime("%d %B %Y")
    )

    replies.append(newReply.model_dump())
    saveAll(replies)
    return newReply
