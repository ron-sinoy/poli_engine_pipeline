from pathlib import Path

def read_text_file(path: str | Path) -> str:
    """Read a UTF-8 text file and fail fast when missing."""
    file_path = Path(path)
    return file_path.read_text(encoding="utf-8")
