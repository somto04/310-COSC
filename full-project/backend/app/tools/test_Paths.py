import pytest
from pathlib import Path
from Paths import get_project_root

def test_path_exists(tmp_path, mocker):
    # Create a fake file structure which resolve will return
    fake_file = tmp_path / "full-project" / "backend" / "app" / "data" / "testfile.py"
    mocker.patch.object(Path, "resolve", return_value=fake_file)

    project_root = get_project_root()
    expected_root = tmp_path / "full-project"
    assert project_root == expected_root

def test_path_not_found(tmp_path, mocker):
    # Create a fake file structure without the full-project directory
    fake_file = tmp_path / "some-other-dir" / "backend" / "app" / "data" / "testfile.py"
    mocker.patch.object(Path, "resolve", return_value=fake_file)

    with pytest.raises(RuntimeError, match="Could not locate project root."):
        get_project_root()
    