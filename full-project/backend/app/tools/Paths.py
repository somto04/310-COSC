from pathlib import Path

def get_project_root() -> Path:
    """
    Return the absolute path to the root of the project directory '.../full-project'.

    Returns:
        Path: The absolute path to the project root.
    
    Raises:
        RuntimeError: If the project root cannot be located.
    """
    path = Path(__file__).resolve()
    for parent in path.parents:
        if parent.name == "full-project":
            return parent
    raise RuntimeError("Could not locate project root.")
