import json
import app.repos.userRepo as userRepo

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
            "role": "substitute_shinigami"
        },
        {
            "id": 2,
            "firstName": "Rukia",
            "lastName": "Kuchiki",
            "age": 150,
            "email": "rukia@soul-society.gov",
            "username": "senpai_rukia",
            "pw": "chappy4life",
            "role": "soul_reaper"
        }
    ]

    test_file.write_text(json.dumps(data))

    # Patch the constant the functions read
    monkeypatch.setattr(userRepo, "USER_DATA_FILE", test_file, raising=False)

    users = userRepo.loadAll()
    assert len(users) == 2
    assert users[0]["id"] == 1
    assert users[0]["firstName"] == "Ichigo"
    assert users[1]["username"] == "senpai_rukia"
    assert users[1]["role"] == "soul_reaper"

def test_user_save_and_verify_contents(tmp_path, monkeypatch):
    test_file = tmp_path / "users.json"
    monkeypatch.setattr(userRepo, "USER_DATA_FILE", test_file, raising=False)

    data = [
        {
            "id": 1,
            "firstName": "Ichigo",
            "lastName": "Kurosaki",
            "age": 17,
            "email": "ichigo@karakura.jp",
            "username": "shinigami17",
            "pw": "getsugatenshou",
            "role": "substitute_shinigami"
        },
        {
            "id": 2,
            "firstName": "Rukia",
            "lastName": "Kuchiki",
            "age": 150,
            "email": "rukia@soul-society.gov",
            "username": "senpai_rukia",
            "pw": "chappy4life",
            "role": "soul_reaper"
        }
    ]

    userRepo.saveAll(data)

    assert test_file.exists(), "users.json should have been created"
    contents = json.loads(test_file.read_text())

    assert contents == data
    assert len(contents) == 2
    assert contents[0]["firstName"] == "Ichigo"
    assert contents[1]["username"] == "senpai_rukia"
    assert contents[1]["role"] == "soul_reaper"
    assert contents[1]["age"] == 150
    