import pytest
from unittest.mock import patch
from app.services import replyService
from app.schemas.reply import ReplyCreate, Reply

# sample fake replies list
fake_replies = [
    Reply(id=1, reviewId=10, userId=1001, replyBody="I agree", datePosted= "1 Jan 2024"),
    Reply(id=2, reviewId=11, userId=1002, replyBody="Nice point!", datePosted="2 Jan 2024")
]

@patch("app.services.replyService.loadReplies")
def test_list_replies_for_review(mock_load):
    mock_load.return_value = fake_replies

    results = replyService.listReplies(10)

    assert len(results) == 1
    assert isinstance(results[0], Reply)
    assert results[0].reviewId == 10
    assert results[0].replyBody == "I agree"


@patch("app.services.replyService.saveReplies")
@patch("app.services.replyService.loadReplies")
def test_create_reply(mock_load, mock_save):
    """ testing creating a new reply (date is required) """
    mock_load.return_value = fake_replies

    payload = ReplyCreate(
        reviewId=12,
        userId=999,
        replyBody="This is a test reply",
        datePosted="3 Jan 2024" 
    )

    new_reply = replyService.createReply(payload)

    assert isinstance(new_reply, Reply)
    assert new_reply.reviewId == 12
    assert new_reply.userId == 999
    assert new_reply.replyBody == "This is a test reply"
    assert new_reply.datePosted == "3 Jan 2024"

    # verify saveAll called with updated data
    mock_save.assert_called_once()
    saved_data = mock_save.call_args[0][0]
    assert any(reply.replyBody == "This is a test reply" for reply in saved_data)
