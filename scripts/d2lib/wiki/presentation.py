from __future__ import annotations

import re
from typing import Any

_MERC_EQUIP_1 = re.compile(r"\b(Helm(?:\s+(?:Eth|Sup|Inf))*?)\s+Merc Equip\b", re.IGNORECASE)
_MERC_EQUIP_2 = re.compile(r"\bMerc Equip\b", re.IGNORECASE)
_SANITIZE_CACHE: dict[str, str] = {}


def sanitize_display_text(value: str) -> str:
    text = value if isinstance(value, str) else str(value)
    # Fast path: the overwhelming majority of strings never mention "Merc Equip".
    if "merc equip" not in text.lower():
        return text
    cached = _SANITIZE_CACHE.get(text)
    if cached is not None:
        return cached
    result = _MERC_EQUIP_1.sub(r"\1", text)
    result = _MERC_EQUIP_2.sub("Helm", result)
    _SANITIZE_CACHE[text] = result
    return result


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
