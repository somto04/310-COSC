import json
import app.repos.userRepo as userRepo
from app.schemas.user import User
from app.schemas.role import Role


def test_user_load_uses_tmp(tmp_path, monkeypatch):
    test_file = tmp_path / "users.json"

    data = [
        {
            "id": 1,
            "firstName": "Ichigo",
            "lastName": "Kurosaki",
            "age": 17,
            "email": "ichigo@karakura.jp",
            "username": "shinigami17",
            "pw": "getsugatenshou",
            "role": Role.USER,
            "penalties": 0,
            "isBanned": False,
        },
        {
            "id": 2,
            "firstName": "Rukia",
            "lastName": "Kuchiki",
            "age": 150,
            "email": "rukia@soul-society.gov",
            "username": "senpai_rukia",
            "pw": "chappy4life",
            "role": Role.ADMIN,
            "penalties": 1,
            "isBanned": False,
        },
    ]

    test_file.write_text(json.dumps(data))

    # Patch the constant the functions read
    monkeypatch.setattr(userRepo, "_USER_DATA_PATH", test_file, raising=False)

    users = userRepo.loadUsers()
    assert len(users) == 2
    assert users[0].id == 1
    assert users[0].firstName == "Ichigo"
    assert users[1].username == "senpai_rukia"
    assert users[1].role == Role.ADMIN
    assert users[1].age == 150
    assert users[1].penalties == 1
    assert users[1].isBanned is False


def test_user_save_and_verify_contents(tmp_path, monkeypatch):
    test_file = tmp_path / "users.json"
    monkeypatch.setattr(userRepo, "_USER_DATA_PATH", test_file, raising=False)

    data = [
        User(
            id=1,
            firstName="Ichigo",
            lastName="Kurosaki",
            age=17,
            email="ichigo@karakura.jp",
            username="shinigami17",
            pw="getsugatenshou",
            role=Role.USER,
            penalties=0,
            isBanned=False,
        ),
        User(
            id=2,
            firstName="Rukia",
            lastName="Kuchiki",
            age=150,
            email="rukia@soul-society.gov",
            username="senpai_rukia",
            pw="chappy4life",
            role=Role.ADMIN,
            penalties=1,
            isBanned=False,
        ),
    ]

    userRepo.saveUsers(data)
    # Now read the file back and verify contents
    with open(test_file, "r") as file:
        saved_data = json.load(file)
    assert len(saved_data) == 2
    assert saved_data[0]["firstName"] == "Ichigo"
    assert saved_data[1]["username"] == "senpai_rukia"
    assert saved_data[1]["role"] == "admin"
    assert saved_data[1]["age"] == 150
    assert saved_data[1]["penalties"] == 1
    assert saved_data[1]["isBanned"] is False


def test_load_users_uses_cache(monkeypatch):
    # arrange: fake base loader & call counter
    calls = {"count": 0}

    def fake_load(path):
        calls["count"] += 1
        return [
            {
                "id": 1,
                "firstName": "A",
                "lastName": "Test",
                "age": 20,
                "email": "a@test.com",
                "username": "a",
                "pw": "x",
                "role": "user",
                "penalties": 0,
                "isBanned": False,
            },
            {
                "id": 2,
                "firstName": "B",
                "lastName": "Test",
                "age": 21,
                "email": "b@test.com",
                "username": "b",
                "pw": "x",
                "role": "user",
                "penalties": 0,
                "isBanned": False,
            },
        ]

    # make sure cache starts clean for this test
    userRepo._USER_CACHE = None

    # patch the low-level loader
    monkeypatch.setattr(userRepo, "_base_load_all", fake_load)

    # act: call twice
    users1 = userRepo.loadUsers()
    users2 = userRepo.loadUsers()

    # assert: underlying load called once
    assert calls["count"] == 1

    # assert: both calls return same object & types are correct
    assert users1 is users2
    assert all(isinstance(u, User) for u in users1)
    assert len(users1) == 2
