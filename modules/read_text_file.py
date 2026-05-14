from pathlib import Path

from modules.progress_log import log_step


def read_text_file(path: str | Path) -> str:
    """Read a UTF-8 text file or return an empty string when missing."""
    file_path = Path(path)
    log_step(f"Reading text file from {file_path}.")
    try:
        contents = file_path.read_text(encoding="utf-8")
        log_step(f"Finished reading text file from {file_path}.")
        return contents
    except FileNotFoundError:
        log_step(f"Text file not found at {file_path}; returning empty string.")
        return ""
