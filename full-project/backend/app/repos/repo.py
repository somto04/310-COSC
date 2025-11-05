import json
from pathlib import Path
from typing import List, Dict, Any

DATA_DIR = Path(__file__).resolve().parents[1] / "data"

def _path(name: str | Path) -> Path:
    """if given a string, return the full path in the data directory;
    provide a Path object to use a custom location."""
    if isinstance(name, Path):
        return name            # already a Path object, no need to wrap
    else:
        return DATA_DIR / name  # join "backend/app/data" with "movies.json"

def _ensure_file(path: Path) -> None:
    """"Ensure the data file exists at the given path."""
    if not path.exists():
        raise FileNotFoundError(f"Missing data file: {path}")
    
def loadAll(datafile: str | Path) -> List[Dict[str, Any]]:
    """"Load all items from the specified data file."""
    path = _path(datafile)
    _ensure_file(path)
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)

def saveAll(datafile: str | Path, items: List[Dict[str, Any]]) -> None:
    """"Save all items to the specified data file."""
    path = _path(datafile)
    path.parent.mkdir(parents=True, exist_ok=True)
    # write into a temporary file first for atomicity
    # so that we don't corrupt the data file if something goes wrong during writing
    temp = path.with_suffix(path.suffix + ".tmp")
    with temp.open("w", encoding="utf-8") as file:
        json.dump(items, file, indent=2, ensure_ascii=False)
    temp.replace(path)  # atomic rename