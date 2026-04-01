"""Shared text helpers for backend usage."""


def truncate(text: str, max_chars: int) -> str:
    """Truncate text while preserving readability."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n\n[Content truncated...]"

