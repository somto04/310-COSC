import pytest
import json

from app.repos.repo import _path, _ensure_file, loadAll, saveAll
from pathlib import Path

@pytest.fixture
def sample_users():
    return [{"id": 1, "name": "Neo"}]

def test_path_with_string():
    data_dir = Path(__file__).resolve().parents[1] / "data"
    result = _path("users.json")
    assert result == data_dir / "users.json"

def test_path_with_path():
    p = Path("/some/path/data.json")
    result = _path(p)
    assert result == p

def test_ensure_file_exists(mocker):
    from app.repos import repo
    mocker.patch.object(repo.Path, "exists", return_value=True)
    path = repo.Path("/some/existing/file.json")
    # Should not raise
    repo._ensure_file(path)

def test_ensure_file_missing(mocker):
    from app.repos import repo
    mocker.patch.object(repo.Path, "exists", return_value=False)
    
    fake = repo.Path("/some/existing/file.json")

    with pytest.raises(FileNotFoundError):
        repo._ensure_file(fake)


def test_load_all(mocker, sample_users):
    from app.repos import repo
    # Mock Path.exists to always return True
    mocker.patch.object(repo.Path, "exists", return_value=True)

    # Mock the open function to return specific JSON data
    m = mocker.mock_open(read_data = json.dumps(sample_users))
    mocker.patch("app.repos.repo.Path.open", m)

    assert repo.loadAll("users.json") == sample_users

    # Assert we opened for read with utf-8
    # Bound method call includes the Path instance as arg[0]
    call = m.mock_calls[0]
    _, args, kwargs = call
    assert args[0] == "r"
    assert kwargs["encoding"] == "utf-8"

def test_load_all_missing_file(mocker):
    from app.repos import repo
    # Mock Path.exists to always return False
    mocker.patch.object(repo.Path, "exists", return_value=False)

    with pytest.raises(FileNotFoundError):
        repo.loadAll("nonexistent.json")

