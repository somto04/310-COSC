from datetime import datetime
from ..schemas.reply import Reply, ReplyCreate
from ..repos.replyRepo import loadReplies, saveReplies

def list_replies(reviewId: int):
    replies = loadReplies()
    return [reply for reply in replies if reply.id == reviewId]

def create_reply(payload: ReplyCreate) -> Reply:
    """ Creates a new reply and adds to json """
    replies = loadReplies()

    newId = max((reply.id for reply in replies), default = 0) + 1

    newReply = Reply(
        id=newId,
        reviewId=payload.reviewId,
        userId=payload.userId,
        replyBody=payload.replyBody.strip() if payload.replyBody else "",
        datePosted=payload.datePosted or datetime.now().strftime("%d %B %Y")
    )

    replies.append(newReply)
    saveReplies(replies)
    return newReply
