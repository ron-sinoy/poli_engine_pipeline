from pathlib import Path

from modules.progress_log import log_step


def read_text_file(path: str | Path) -> str:
    """Read a UTF-8 text file and fail fast when missing."""
    file_path = Path(path)
    log_step(f"Reading text file from {file_path}.")
    contents = file_path.read_text(encoding="utf-8")
    log_step(f"Finished reading text file from {file_path}.")
    return contents
