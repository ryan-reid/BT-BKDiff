import re

def get_group_for_category(category: str) -> str:
    category_lower = category.lower()
    if category_lower in ['expansion', 'other']:
        return 'other'
    
    # Weapons
    if any(w in category_lower for w in ['axe', 'bow', 'club', 'crossbow', 'hammer', 'javelin', 'knife', 'mace', 'polearm', 'scepter', 'spear', 'staff', 'sword', 'throwing', 'wand', 'weapon']):
        return 'weapons'
    
    # Armor
    if any(a in category_lower for a in ['armor', 'belt', 'boots', 'gloves', 'circlet', 'helm', 'shield']):
        return 'armor'
        
    # Accessories
    if any(acc in category_lower for acc in ['amulet', 'ring', 'charm', 'jewel']):
        return 'accessories'
        
    # Class Specific
    if any(cls in category_lower for cls in ['amazon', 'auric', 'grimoire', 'hand to hand', 'orb', 'pelt', 'primal', 'voodoo']):
        return 'class_specific'
        
    return 'other'

print(f"Merc Equip -> {get_group_for_category('Merc Equip')}")
print(f"Helm -> {get_group_for_category('Helm')}")
