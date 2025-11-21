import pytest
from fastapi.testclient import TestClient
from app.app import app
from app.routers import replyRoute
from app.repos import replyRepo

# Fake login dependency
app.dependency_overrides[replyRoute.getCurrentUser] = lambda: {
    "id": 1,
    "username": "tester",
    "role": "admin"
}


@pytest.fixture(autouse=True)
def mockRepos(monkeypatch):
    """Prevent touching the real replies.json."""
    fakeData = []

    def fakeLoadAll():
        return fakeData

    def fakeSaveAll(data):
        fakeData.clear()
        fakeData.extend(data)
        return True

    monkeypatch.setattr(replyRepo, "loadAll", fakeLoadAll)
    monkeypatch.setattr(replyRepo, "saveAll", fakeSaveAll)

@pytest.fixture
def client(mockRepos):
    return TestClient(app)

def test_getReplies(client):
    """Checks that /replies/{reviewId} returns a valid response (even if empty)."""
    response = client.get("/replies/1")

    # route should exist
    assert response.status_code in [200, 404]

    if response.status_code == 200:
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            assert "replyBody" in data[0]
            assert "userId" in data[0]


def test_postReply(client):
    """Checks that /replies accepts new replies correctly."""
    payload = {
        "reviewId": 1,
        "userId": 100,
        "replyBody": "This is a simple test reply!",
        "datePosted": "3 Nov 2025"
    }

    response = client.post("/replies", json=payload)
    assert response.status_code in [200, 201]

    data = response.json()
    assert data["replyBody"] == payload["replyBody"]
    assert data["userId"] == payload["userId"]
    assert data["reviewId"] == payload["reviewId"]
