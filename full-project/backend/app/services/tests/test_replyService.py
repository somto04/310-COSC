import pytest
from unittest.mock import patch
from app.services import replyService
from app.schemas.reply import ReplyCreate, Reply

# sample fake replies list
fakeReplies = [
    Reply(id=1, reviewId=1, userId=1001, replyBody="I agree", datePosted= "1 Jan 2024"),
    Reply(id=2, reviewId=2, userId=1002, replyBody="Nice point!", datePosted="2 Jan 2024")
]

@patch("app.services.replyService.loadReplies")
def test_listRepliesForReview(mockLoad):
    mockLoad.return_value = fakeReplies

    results = replyService.listReplies(1)

    assert len(results) == 1
    assert isinstance(results[0], Reply)
    assert results[0].reviewId == 1
    assert results[0].replyBody == "I agree"


@patch("app.services.replyService.saveReplies")
@patch("app.services.replyService.loadReplies")
def test_createReply(mockLoad, mockSave):
    """ testing creating a new reply (date is required) """
    mockLoad.return_value = fakeReplies

    payload = ReplyCreate(
        reviewId=12,
        userId=999,
        replyBody="This is a test reply",
        datePosted="3 Jan 2024" 
    )

    newReply = replyService.createReply(payload)

    assert isinstance(newReply, Reply)
    assert newReply.reviewId == 12
    assert newReply.userId == 999
    assert newReply.replyBody == "This is a test reply"
    assert newReply.datePosted == "3 Jan 2024"

    # verify saveAll called with updated data
    mockSave.assert_called_once()
    saved_data = mockSave.call_args[0][0]
    assert any(reply.replyBody == "This is a test reply" for reply in saved_data)
