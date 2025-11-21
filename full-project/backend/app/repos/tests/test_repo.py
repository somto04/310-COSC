import json
from pathlib import Path

import pytest

from app.tools.Paths import getProjectRoot
from app.tools.Paths import getProjectRoot
from app.repos import repo


@pytest.fixture
def sampleItems():
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
    result = repo._fullPath("users.json")
    assert result == expectedDir / "users.json"


def test_pathWithPath():
    testPath = Path("/some/path/data.json")
    result = repo._fullPath(testPath)
    assert result is testPath


def test_ensureFileExists(tmp_path):
    path = tmp_path / "exists.json"
    path.write_text("[]", encoding="utf-8")

    # should not raise
    repo._ensureFile(path)


def test_ensureFileMissing(tmp_path):
    path = tmp_path / "missing.json"

    with pytest.raises(FileNotFoundError):
        repo._ensureFile(path)


def test_baseLoadAllReadsJson(tmp_path, monkeypatch, sampleItems):
    # point DATA_DIR at a temporary directory
    monkeypatch.setattr(repo, "DATA_DIR", tmp_path)

    path = tmp_path / "users.json"
    path.write_text(json.dumps(sampleItems), encoding="utf-8")

    result = repo._baseLoadAll("users.json")

    assert result == sampleItems


def test_baseLoadAllMissingFile(tmp_path, monkeypatch):
    monkeypatch.setattr(repo, "DATA_DIR", tmp_path)

    with pytest.raises(FileNotFoundError):
        repo._baseLoadAll("nonexistent.json")


def test_baseSaveAllWritesFileAuto(tmp_path, monkeypatch, sampleItems):
    # redirect DATA_DIR so we don't touch real project files
    monkeypatch.setattr(repo, "DATA_DIR", tmp_path)

    repo._baseSaveAll("users.json", sampleItems)

    dataPath = tmp_path / "users.json"
    tmpPathFile = tmp_path / "users.json.tmp"

    # file was written
    assert dataPath.exists()

    # no leftover temp file after replace
    assert not tmpPathFile.exists()

    # content is correct JSON
    loaded = json.loads(dataPath.read_text(encoding="utf-8"))
    assert loaded == sampleItems
