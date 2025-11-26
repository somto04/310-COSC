from datetime import datetime
from ..schemas.reply import Reply, ReplyCreate
from ..repos.replyRepo import loadReplies, saveReplies, getNextReplyId
from ..repos.reviewRepo import loadReviews
from ..services.reviewService import getReviewById

class ReviewNotFoundError(Exception):
    pass



def listReplies(reviewId: int):
    """ Lists all replies for a given review """
    review = getReviewById(reviewId)
    if review is None:
    
        raise ReviewNotFoundError(f"Review with id {reviewId} not found.")

    replies = loadReplies()
    return [reply for reply in replies if reply.reviewId == reviewId]

def createReply(payload: ReplyCreate) -> Reply:
    """ Creates a new reply and adds to json """
    replies = loadReplies()

    newReply = Reply(
        id=getNextReplyId(),
        reviewId=payload.reviewId,
        userId=payload.userId,
        replyBody=payload.replyBody.strip() if payload.replyBody else "",
        datePosted=payload.datePosted or datetime.now().strftime("%d %B %Y")
    )

    replies.append(newReply)
    saveReplies(replies)
    return newReply
