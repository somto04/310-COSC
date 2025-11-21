import pytest
from unittest.mock import patch
from app.services import replyService
from app.schemas.review import ReplyCreate, Reply

# sample fake replies list
fakeReplies = [
    {"id": 1, "reviewId": 10, "userId": 1001, "replyBody": "I agree", "datePosted": "1 Jan 2024"},
    {"id": 2, "reviewId": 11, "userId": 1002, "replyBody": "Nice point!", "datePosted": "2 Jan 2024"},
]

# testing listing replies for a review
@patch("app.services.replyService.loadAll")
def test_listRepliesForReview(mockLoad):
    mockLoad.return_value = fakeReplies

    results = replyService.listReplies(10)

    assert len(results) == 1
    assert isinstance(results[0], Reply)
    assert results[0].reviewId == 10
    assert results[0].replyBody == "I agree"


# testing creating a new reply (date is required)
@patch("app.services.replyService.saveAll")
@patch("app.services.replyService.loadAll")
def test_createReply(mockLoad, mockSave):
    mockLoad.return_value = fakeReplies

    payload = ReplyCreate(
        reviewId=12,
        userId=999,
        replyBody="This is a test reply",
        datePosted="3 Jan 2024"   # now provided
    )

    newReply = replyService.createReply(payload)

    # returned object type and fields
    assert isinstance(newReply, Reply)
    assert newReply.reviewId == 12
    assert newReply.userId == 999
    assert newReply.replyBody == "This is a test reply"
    assert newReply.datePosted == "3 Jan 2024"

    # verify saveAll called with updated data
    mockSave.assert_called_once()
    savedData = mockSave.call_args[0][0]
    assert any(r["replyBody"] == "This is a test reply" for r in savedData)
