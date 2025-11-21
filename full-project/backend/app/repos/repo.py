import json
from pathlib import Path
from typing import List, Dict, Any
from app.tools.Paths import getProjectRoot

DATA_DIR = getProjectRoot() / "backend" / "app" / "data"

def fullPath(name: str | Path) -> Path:
    """
    Get the full path to the data file.

    Args:
        name (str | Path): The name of the data file or a Path object.

    Returns:
        Path: The full Path to the data file.
    """
    if isinstance(name, Path):
        return name
    else:
        return DATA_DIR / name

def ensureFile(path: Path) -> None:
    """
    Ensure that the specified file exists.
    
    Args:
        path (Path): The path to the file to check.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    if not path.exists():
        raise FileNotFoundError(f"Missing data file: {path}")
    
def baseLoadAll(datafile: str | Path) -> List[Dict[str, Any]]:
    """
    Load all items from the specified data file.
    
    Args:
        datafile (str | Path): The name of the data file or a Path object.

    Returns:
        List[Dict[str, Any]]: A list of items loaded from the data file.
    """
    path = fullPath(datafile)
    ensureFile(path)
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)

def baseSaveAll(datafile: str | Path, items: List[Dict[str, Any]]) -> None:
    """
    Save all items to the specified data file.
    
    Atomically writes to a temporary file first to avoid data corruption.
    Args:
        datafile (str | Path): The name of the data file or a Path object.
        items (List[Dict[str, Any]]): A list of items to save.
    """
    path = fullPath(datafile)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    temp = path.with_suffix(path.suffix + ".tmp")
    
    with temp.open("w", encoding="utf-8") as file:
        json.dump(items, file, indent=2, ensure_ascii=False)
    
    temp.replace(path)