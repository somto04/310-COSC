import json
from pathlib import Path

import pytest

from app.tools.Paths import get_project_root
from app.repos import repo


@pytest.fixture
def sample_items():
    return [
        {
            "id": 1,
            "username": "test",
            "email": "test@example.com",
            "age": 25,
            "role": "user",
            "penalties": 0,
            "isBanned": False,
            "firstName": "Test",
            "lastName": "User",
            "pw": "hashedPassword25",
        }
    ]


def test_path_with_string():
    expected_dir = get_project_root() / "backend" / "app" / "data"
    result = repo._path("users.json")
    assert result == expected_dir / "users.json"


def test_path_with_path():
    test_path = Path("/some/path/data.json")
    result = repo._path(test_path)
    assert result is test_path


def test_ensure_file_exists(tmp_path):
    path = tmp_path / "exists.json"
    path.write_text("[]", encoding="utf-8")

    # should not raise
    repo._ensure_file(path)


def test_ensure_file_missing(tmp_path):
    path = tmp_path / "missing.json"

    with pytest.raises(FileNotFoundError):
        repo._ensure_file(path)


def test_base_load_all_reads_json(tmp_path, monkeypatch, sample_items):
    # point DATA_DIR at a temporary directory
    monkeypatch.setattr(repo, "DATA_DIR", tmp_path)

    path = tmp_path / "users.json"
    path.write_text(json.dumps(sample_items), encoding="utf-8")

    result = repo._base_load_all("users.json")

    assert result == sample_items


def test_base_load_all_missing_file(tmp_path, monkeypatch):
    monkeypatch.setattr(repo, "DATA_DIR", tmp_path)

    with pytest.raises(FileNotFoundError):
        repo._base_load_all("nonexistent.json")


def test_base_save_all_writes_file_atomically(tmp_path, monkeypatch, sample_items):
    # redirect DATA_DIR so we don't touch real project files
    monkeypatch.setattr(repo, "DATA_DIR", tmp_path)

    repo._base_save_all("users.json", sample_items)

    data_path = tmp_path / "users.json"
    tmp_path_file = tmp_path / "users.json.tmp"

    # file was written
    assert data_path.exists()

    # no leftover temp file after replace
    assert not tmp_path_file.exists()

    # content is correct JSON
    loaded = json.loads(data_path.read_text(encoding="utf-8"))
    assert loaded == sample_items
