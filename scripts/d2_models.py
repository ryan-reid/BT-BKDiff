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
    properties: List[PropertyDTO]
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
    inputs: List[str]
    outputs: List[str]
    raw_row: Dict[str, str]
