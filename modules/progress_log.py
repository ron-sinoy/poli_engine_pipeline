from typing import Any


def log_step(message: str) -> None:
    print(f"[pipeline] {message}", flush=True)


def describe_payload(payload: Any) -> str:
    #Return a short human-readable payload summary for logs
    if isinstance(payload, list):
        return f"list(len={len(payload)})"

    if isinstance(payload, dict):
        return f"dict(keys={len(payload)})"

    if isinstance(payload, str):
        return f"str(len={len(payload)})"

    if payload is None:
        return "None"

    return type(payload).__name__
