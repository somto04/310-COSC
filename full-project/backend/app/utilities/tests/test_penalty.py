import pytest
from app.utilities.penalties import incrementPenaltyForUser
from app.schemas.user import User

def test_IncrementPenalty(monkeypatch):
    # fake user data
    fake_users = [
        User(id=1, username="test", email="x", password="y", age=20, 
             role="user",penalties=0, isBanned=False)
    ]

    
    monkeypatch.setattr(
        "app.utilities.penalties.loadUsers",
        lambda: fake_users
    )

    
    saved = []
    monkeypatch.setattr(
        "app.utilities.penalties.saveUsers",
        lambda users: saved.extend(users)
    )

    updated = incrementPenaltyForUser(1)

    assert updated.penalties == 1
    assert updated.isBanned is False
    assert saved[0].penalties == 1

def test_IncrementPenaltyBan(monkeypatch):
    # fake user data
    fake_users = [
        User(id=2, username="test", email="x", password="y", age=20, role="user",
             penalties=2, isBanned=False)
    ]

    
    monkeypatch.setattr(
        "app.utilities.penalties.loadUsers",
        lambda: fake_users
    )

    
    saved = []
    monkeypatch.setattr(
        "app.utilities.penalties.saveUsers",
        lambda users: saved.extend(users)
    )

    updated = incrementPenaltyForUser(2)

    assert updated.penalties == 3
    assert updated.isBanned is True
    assert saved[0].penalties == 3
    assert saved[0].isBanned is True

