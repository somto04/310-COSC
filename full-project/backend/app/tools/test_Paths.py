import pytest
from pathlib import Path
from app.tools.Paths import getProjectRoot


def test_pathExists(tmp_path, mocker):
    # Create a fake file structure which resolve will return
    fakeFile = tmp_path / "full-project" / "backend" / "app" / "data" / "testfile.py"
    mocker.patch.object(Path, "resolve", return_value=fakeFile)

    projectRoot = getProjectRoot()
    expectedRoot = tmp_path / "full-project"
    assert projectRoot == expectedRoot

def test_pathNotFound(tmp_path, mocker):
    # Create a fake file structure without the full-project directory
    fakeFile = tmp_path / "some-other-dir" / "backend" / "app" / "data" / "testfile.py"
    mocker.patch.object(Path, "resolve", return_value=fakeFile)

    with pytest.raises(RuntimeError, match="Could not locate project root."):
        getProjectRoot()
        getProjectRoot()
    