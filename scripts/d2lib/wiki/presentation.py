from __future__ import annotations

from typing import Any


def sanitize_display_text(value: str) -> str:
    """Identity formatter kept for backwards compatibility; no string rewriting is performed."""
    return value if isinstance(value, str) else str(value)


def sanitize_display_payload(value: Any) -> Any:
    """Identity helper kept for backwards compatibility; payloads pass through unchanged."""
    return value
