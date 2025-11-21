import pytest
from app.utilities.penalties import incrementPenaltyForUser
from app.schemas.user import User
from app.schemas.role import Role


def test_IncrementPenalty(monkeypatch):
    # fake user data
    fakeUsers = [
        User(
            id=1,
            username="test",
            email="sigma@example.com",
            age=20,
            role=Role.USER,
            penalties=0,
            isBanned=False,
            firstName="Test",
            lastName="User",
            pw="hashedSigma21",
        )
    ]

    monkeypatch.setattr("app.utilities.penalties.loadUsers", lambda: fakeUsers)

    saved = []
    monkeypatch.setattr(
        "app.utilities.penalties.saveUsers", lambda users: saved.extend(users)
    )

    updated = incrementPenaltyForUser(1)

    assert updated.penalties == 1
    assert updated.isBanned is False
    assert saved[0].penalties == 1


def test_IncrementPenaltyBan(monkeypatch):
    # fake user data
    fakeUsers = [
        User(
            id=2,
            username="beta",
            email="beta@example.com",
            age=20,
            role=Role.USER,
            penalties=2,
            isBanned=False,
            firstName="Beta",
            lastName="Tester",
            pw="hashedBeta22",
        )
    ]

    monkeypatch.setattr("app.utilities.penalties.loadUsers", lambda: fakeUsers)

    saved = []
    monkeypatch.setattr(
        "app.utilities.penalties.saveUsers", lambda users: saved.extend(users)
    )

    updated = incrementPenaltyForUser(2)

    assert updated.penalties == 3
    assert updated.isBanned is True
    assert saved[0].penalties == 3
    assert saved[0].isBanned is True
