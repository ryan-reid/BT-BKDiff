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

def item_category_to_group(category: str) -> str:
    """Maps a D2 item category string to its display group name."""
    cat = category.lower()
    if any(cls in cat for cls in ['amazon', 'assassin', 'orb', 'hand to hand', 'grimoire']):
        return 'Class Weapons'
    if 'axe' in cat: return 'Axes'
    if 'crossbow' in cat: return 'Crossbows'  # must precede 'bow'
    if 'bow' in cat: return 'Bows'
    if 'dagger' in cat or 'knife' in cat: return 'Daggers'
    if 'javelin' in cat: return 'Javelins'
    if 'mace' in cat or 'club' in cat or 'hammer' in cat: return 'Maces'
    if 'polearm' in cat: return 'Polearms'
    if 'scepter' in cat: return 'Scepters'
    if 'spear' in cat: return 'Spears'
    if 'staff' in cat: return 'Staves'
    if 'sword' in cat: return 'Swords'
    if 'throwing' in cat: return 'Throwing'
    if 'wand' in cat: return 'Wands'
    if any(cls in cat for cls in ['voodoo', 'pelt', 'primal', 'auric']): return 'Class Armors'
    if 'amulet' in cat: return 'Amulets'
    if 'ring' in cat: return 'Rings'
    if 'charm' in cat: return 'Charms'
    if 'jewel' in cat: return 'Jewels'
    if any(h in cat for h in ['helm', 'circlet', 'merc']): return 'Helms'
    if any(c in cat for c in ['armor', 'tors']): return 'Chests'
    if 'shield' in cat: return 'Shields'
    if 'glove' in cat: return 'Gloves'
    if 'belt' in cat: return 'Belts'
    if 'boot' in cat: return 'Boots'
    return 'Others'

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