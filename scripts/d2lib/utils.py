from __future__ import annotations
import re

def slugify(value: str) -> str:
    """Converts a string to a URL-friendly slug."""
    text = value.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[-+\s]+", "-", text)
    return text.strip("-") or "untitled"

def strip_markdown(value: str) -> str:
    """Removes basic markdown formatting from a string."""
    text = value.replace("\\+", "+")
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"`(.*?)`", r"\1", text)
    return text.strip()

def normalize_d2_text(s: str) -> str:
    """Normalizes Diablo II specific characters and encoding artifacts."""
    if not s: return ""
    # Remove color codes
    s = re.sub(r'ÿc.', '', s)
    # Normalize bullet points and markup
    s = s.replace('•', '').replace('**', '')
    # Normalize common phrases
    s = s.replace("Physical Damage Received Reduced by", "Damage Reduced by")
    s = re.sub(r'(Original|Random) Class', 'Random Class', s, flags=re.IGNORECASE)
    # Collapse whitespace
    s = re.sub(r'\s+', ' ', s)
    return s.strip()