import json
from pathlib import Path

import pytest

from app.tools.Paths import getProjectRoot
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


def test_pathWithString():
    expectedDir = getProjectRoot() / "backend" / "app" / "data"
    result = repo.fullPath("users.json")
    assert result == expectedDir / "users.json"


def test_pathWithPath():
    testPath = Path("/some/path/data.json")
    result = repo.fullPath(testPath)
    assert result is testPath


def test_ensureFileExists(tmp_path):
    path = tmp_path / "exists.json"
    path.write_text("[]", encoding="utf-8")

    # should not raise
    repo.ensureFile(path)


def test_ensureFileMissing(tmp_path):
    path = tmp_path / "missing.json"

    with pytest.raises(FileNotFoundError):
        repo.ensureFile(path)


def test_baseLoadAllReadsJson(tmp_path, monkeypatch, sample_items):
    # point DATA_DIR at a temporary directory
    monkeypatch.setattr(repo, "DATA_DIR", tmp_path)

    path = tmp_path / "users.json"
    path.write_text(json.dumps(sample_items), encoding="utf-8")

    result = repo.baseLoadAll("users.json")

    assert result == sample_items


def test_baseLoadAllMissingFile(tmp_path, monkeypatch):
    monkeypatch.setattr(repo, "DATA_DIR", tmp_path)

    with pytest.raises(FileNotFoundError):
        repo.baseLoadAll("nonexistent.json")


def test_baseSaveAllWritesFileAuto(tmp_path, monkeypatch, sample_items):
    # redirect DATA_DIR so we don't touch real project files
    monkeypatch.setattr(repo, "DATA_DIR", tmp_path)

    repo.baseSaveAll("users.json", sample_items)

    data_path = tmp_path / "users.json"
    tmp_path_file = tmp_path / "users.json.tmp"

    # file was written
    assert data_path.exists()

    # no leftover temp file after replace
    assert not tmp_path_file.exists()

    # content is correct JSON
    loaded = json.loads(data_path.read_text(encoding="utf-8"))
    assert loaded == sample_items
