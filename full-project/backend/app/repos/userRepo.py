# ...existing code...
import json
from pathlib import Path
from typing import List, Dict

DATA_FILE = Path(__file__).resolve().parents[2] / "data" / "users.json"

def _ensure_file():
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Missing data file: {DATA_FILE}")

def loadAll() -> List[Dict]:
    _ensure_file()
    with DATA_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)

def saveAll(items: List[Dict]) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with DATA_FILE.open("w", encoding="utf-8") as f:
        json.dump(items, f, indent=2, ensure_ascii=False)
# ...existing code...