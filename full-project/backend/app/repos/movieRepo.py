# ...existing code...
import json
from pathlib import Path
from typing import List, Dict

DATA_FILE = Path(__file__).resolve().parent / "movies.json"

def _ensure_file():
    if not DATA_FILE.exists():
        DATA_FILE.write_text("[]", encoding="utf-8")

def loadAll() -> List[Dict]:
    _ensure_file()
    with DATA_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)

def saveAll(movies: List[Dict]) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with DATA_FILE.open("w", encoding="utf-8") as f:
        json.dump(movies, f, indent=2, ensure_ascii=False)
# ...existing code...