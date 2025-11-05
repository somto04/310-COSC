from pathlib import Path

def get_project_root() -> Path:
    path = Path(__file__).resolve()
    for parent in path.parents:
        if parent.name == "full-project":
            return parent
    raise RuntimeError("Could not locate project root.")
