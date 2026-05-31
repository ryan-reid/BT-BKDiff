from typing import List, Dict, TypedDict, Optional, Any

class PropertyDTO(TypedDict):
    code: str
    param: str
    min_val: str
    max_val: str
    resolved_text: str

class AnalyzedItemDTO(TypedDict):
    id: str
    display_name: str
    base_item: str
    item_type: str
    lvl_req: str
    properties: List[PropertyDTO]
    raw_row: Dict[str, str]

class RunewordDTO(TypedDict):
    name: str
    runes: List[str]
    base_items: List[str]
    required_level: str
    properties: List[PropertyDTO]
    rune_properties: List[Dict[str, Any]]
    raw_row: Dict[str, str]

class ExcelDiffRowDTO(TypedDict):
    bk_new: Any
    bt_old: Any

class ExcelDiffDTO(TypedDict):
    filename: str
    key_used: str
    added_cols: List[str]
    removed_cols: List[str]
    added_rows: List[str]
    removed_rows: List[str]
    modified_rows: Dict[str, Dict[str, ExcelDiffRowDTO]]

class ItemDiffDTO(TypedDict):
    added: Dict[str, AnalyzedItemDTO]
    removed: Dict[str, AnalyzedItemDTO]
    modified: Dict[str, Dict[str, Any]] # Detailed diff structure

class CubeRecipeDTO(TypedDict):
    id: str
    description: str
    enabled: bool
    status: str
    inputs: List[str]
    outputs: List[str]
    raw_row: Dict[str, str]

class CubeRecipeGroupDTO(TypedDict):
    id: str
    name: str
    summary: str
    action: str
    order: int
    status_counts: Dict[str, int]
    corruption_summaries: List[Dict[str, Any]]
    recipes: List[CubeRecipeDTO]

class SkillEffectDTO(TypedDict):
    label: str
    scaling: str
    l1: str
    l10: str
    l20: str
    l30: str
    limit: str

class SkillSynergyDTO(TypedDict):
    name: str
    effect: str

class SkillDTO(TypedDict):
    id: str
    name: str
    effects: List[SkillEffectDTO]
    synergies: List[SkillSynergyDTO]
    raw_row: Dict[str, str]

class SkillTreeDTO(TypedDict):
    class_name: str
    skills: List[SkillDTO]

class BaseItemDTO(TypedDict):
    code: str
    name: str
    icon_key: str
    icon_src: str
    type: str
    type_categories: List[str]
    level: int
    level_req: int
    defense_min: Optional[int]
    defense_max: Optional[int]
    damage_min: Optional[int]
    damage_max: Optional[int]
    two_hand_damage_min: Optional[int]
    two_hand_damage_max: Optional[int]
    two_handed_only: bool
    str_req: int
    dex_req: int
    block: int
    sockets: int
    max_sockets_by_ilvl: Dict[str, int]
    class_restriction: str
    staffmod_class: str
    magic_level: int
    inherent_stats: List[str]
    auto_prefix_stats: List[str]
    auto_prefix_summary: List[str]
    quality_bonus_stats: List[str]
    quality_bonus_summary: List[str]
    speed: int
    speed_label: str
    durability: int
    tier: str # Normal, Exceptional, Elite

class BaseItemFamilyDTO(TypedDict):
    name: str
    group: str
    summary: str
    class_tags: List[str]
    max_sockets: int
    search_text: str
    members: List[BaseItemDTO]

class MonsterDTO(TypedDict):
    id: str
    name: str
    level_norm: int
    level_nm: int
    level_hell: int
    hp_norm: str
    hp_nm: str
    hp_hell: str
    resists_hell: Dict[str, int]
    immunities_hell: List[str]
    spawn_areas: List[str]
    is_boss: bool
    is_unique: bool
    status: str
    changed_fields: List[str]

class MonsterActGroupDTO(TypedDict):
    act: str
    monsters: List[MonsterDTO]

class MiscItemDTO(TypedDict):
    code: str
    name: str
    icon_key: str
    icon_src: str
    type: str
    level: int
    level_req: int
    stackable: bool
    max_stack: int
    cost: int
    description: str
    category: str
    status: str
    socket_effects: Dict[str, List[str]]

class MiscGroupDTO(TypedDict):
    category: str
    summary: str
    order: int
    source_categories: List[str]
    members: List[MiscItemDTO]

class MechanicsSummaryDTO(TypedDict):
    experience_changes: List[Dict[str, Any]]
    difficulty_changes: List[Dict[str, Any]]
    skill_changes: List[Dict[str, Any]]
    missile_changes: List[Dict[str, Any]]
    charstat_changes: List[Dict[str, Any]]
    property_changes: List[Dict[str, Any]]
    itemstat_changes: List[Dict[str, Any]]
    gamble_changes: List[Dict[str, Any]]
