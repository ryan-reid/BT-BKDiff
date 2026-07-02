from __future__ import annotations

import re
from typing import Any


def sanitize_display_text(value: str) -> str:
    text = str(value)
    text = re.sub(
        r"\b(Helm(?:\s+(?:Eth|Sup|Inf))*?)\s+Merc Equip\b",
        r"\1",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(r"\bMerc Equip\b", "Helm", text, flags=re.IGNORECASE)
    return text


def sanitize_display_payload(value: Any) -> Any:
    if isinstance(value, str):
        return sanitize_display_text(value)
    if isinstance(value, list):
        return [sanitize_display_payload(item) for item in value]
    if isinstance(value, tuple):
        return tuple(sanitize_display_payload(item) for item in value)
    if isinstance(value, dict):
        return {
            key: sanitize_display_payload(item)
            for key, item in value.items()
        }
    return value
