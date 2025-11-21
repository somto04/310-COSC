import pytest
from fastapi.testclient import TestClient
from app.app import app
from app.routers import replyRoute
from app.repos import replyRepo
from ...schemas.reply import Reply
from app.routers import auth
from app.schemas.user import CurrentUser
from app.schemas.role import Role


@pytest.fixture(autouse=True)
def fakeLogin():
    """Pretend every request is authenticated as an admin user."""
    fakeUser = CurrentUser(
        id=1,
        username="tester",
        role=Role.ADMIN,
    )
    app.dependency_overrides[auth.getCurrentUser] = lambda: fakeUser
    yield
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def mock_repos(monkeypatch):
    """Prevent touching the real replies.json."""
    fakeData = [
        Reply(
            id=1, reviewId=1, userId=1001, replyBody="I agree", datePosted="1 Jan 2024"
        ),
        Reply(
            id=2,
            reviewId=2,
            userId=1002,
            replyBody="Nice point!",
            datePosted="2 Jan 2024",
        ),
    ]

    def fakeLoadReplies():
        return fakeData

    def fakeSaveReplies(data):
        fakeData.clear()
        fakeData.extend(data)
        return True

    monkeypatch.setattr(replyRepo, "loadReplies", fakeLoadReplies)
    monkeypatch.setattr(replyRepo, "saveReplies", fakeSaveReplies)
    monkeypatch.setattr("app.services.replyService.loadReplies", fakeLoadReplies)
    monkeypatch.setattr("app.services.replyService.saveReplies", fakeSaveReplies)


@pytest.fixture
def client(mock_repos):
    return TestClient(app)


def test_get_replies(client):
    """Checks that /replies/{reviewId} returns a valid response (even if empty)."""
    response = client.get("/replies/1")

    assert response.status_code in [200, 404]

    if response.status_code == 200:
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            assert "replyBody" in data[0]
            assert "userId" in data[0]


def test_post_reply(client):
    """Checks that /replies accepts new replies correctly."""
    payload = {
        "reviewId": 1,
        "userId": 100,
        "replyBody": "This is a simple test reply!",
        "datePosted": "3 Nov 2025",
    }

    response = client.post("/replies", json=payload)
    assert response.status_code in [200, 201]

    data = response.json()
    assert data["replyBody"] == payload["replyBody"]
    assert data["userId"] == payload["userId"]
    assert data["reviewId"] == payload["reviewId"]
