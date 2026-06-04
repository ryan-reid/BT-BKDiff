from __future__ import annotations
import os
import re

ITEM_FAMILIES = ("unique", "set", "runeword")
DAMAGE_TYPES = (
    ("physical", "ResDm(H)"),
    ("magic", "ResMa(H)"),
    ("fire", "ResFi(H)"),
    ("lightning", "ResLi(H)"),
    ("cold", "ResCo(H)"),
    ("poison", "ResPo(H)"),
)
REPORT_SOURCES = (
    {
        "title": "Item Diff: BKDiablo vs Retail",
        "description": "Item database changes comparing BKDiablo against retail data.",
        "source_dir": "item_diff_report_retail_bk",
        "output_dir": "reports/items/retail-bk",
        "source_kind": "item_diff",
    },
    {
        "title": "Item Diff: BKDiablo vs BTDiablo",
        "description": "Item database changes comparing BKDiablo against BTDiablo.",
        "source_dir": "item_diff_report_bt_bk",
        "output_dir": "reports/items/bt-bk",
        "source_kind": "item_diff",
    },
    {
        "title": "Excel Diff: BKDiablo vs Retail",
        "description": "Raw Excel table changes comparing BKDiablo against retail data.",
        "source_dir": "excel_diff_report_retail_bk",
        "output_dir": "reports/excel/retail-bk",
        "source_kind": "excel_diff",
    },
    {
        "title": "Override File Diff: BKDiablo vs Retail",
        "description": "Text and JSON override file changes comparing BKDiablo against retail files.",
        "source_dir": "file_diff_report_retail_bk",
        "output_dir": "reports/files/retail-bk",
        "source_kind": "file_diff",
    },
    {
        "title": "Excel Diff: BKDiablo vs BTDiablo",
        "description": "Raw Excel table changes comparing BKDiablo against BTDiablo.",
        "source_dir": "excel_diff_report_bt_bk",
        "output_dir": "reports/excel/bt-bk",
        "source_kind": "excel_diff",
    },
)

from d2lib.utils import slugify, strip_markdown

class WikiRoutes:
    @staticmethod
    def home_output_path() -> str:
        return "index.html"

    @staticmethod
    def items_index_output_path() -> str:
        return "items/index.html"

    @staticmethod
    def sets_index_output_path() -> str:
        return "sets/index.html"

    @staticmethod
    def runewords_index_output_path() -> str:
        return "runewords/index.html"

    @staticmethod
    def bases_index_output_path() -> str:
        return "bases/index.html"

    @staticmethod
    def base_item_output_path(slug: str) -> str:
        return f"bases/{slug}/index.html"

    @staticmethod
    def recipes_index_output_path() -> str:
        return "recipes/index.html"

    @staticmethod
    def recipes_crafting_output_path() -> str:
        return "recipes/crafting/index.html"

    @staticmethod
    def recipes_corruptions_output_path() -> str:
        return "recipes/corruptions/index.html"

    @staticmethod
    def recipes_pierce_output_path() -> str:
        return "recipes/pierce/index.html"

    @staticmethod
    def recipes_reforge_upgrade_output_path() -> str:
        return "recipes/reforge-upgrade/index.html"

    @staticmethod
    def recipes_materials_output_path() -> str:
        return "recipes/materials/index.html"

    @staticmethod
    def recipes_all_output_path() -> str:
        return "recipes/all/index.html"

    @staticmethod
    def recipes_raw_output_path() -> str:
        return "recipes/raw/index.html"

    @staticmethod
    def bestiary_index_output_path() -> str:
        return "bestiary/index.html"

    @staticmethod
    def misc_index_output_path() -> str:
        return "misc/index.html"

    @staticmethod
    def gems_runes_index_output_path() -> str:
        return "gems-runes/index.html"

    @staticmethod
    def gem_rune_output_path(slug: str) -> str:
        return f"gems-runes/{slug}/index.html"

    @staticmethod
    def mechanics_output_path() -> str:
        return "mechanics/index.html"

    @staticmethod
    def drops_index_output_path() -> str:
        return "drops/index.html"

    @staticmethod
    def item_output_path(family: str, slug: str) -> str:
        return f"items/{family}/{slug}/index.html"

    @staticmethod
    def classes_index_output_path() -> str:
        return "classes/index.html"

    @staticmethod
    def areas_index_output_path() -> str:
        return "areas/index.html"

    @staticmethod
    def class_output_path(slug: str) -> str:
        return f"classes/{slug}/index.html"

    @staticmethod
    def patch_notes_output_path() -> str:
        return "patch-notes/full-patch-notes-draft/index.html"

    @staticmethod
    def reports_index_output_path() -> str:
        return "reports/index.html"

    @staticmethod
    def route_from_output_path(output_path: str) -> str:
        normalized = output_path.replace("\\", "/")
        if normalized == "index.html":
            return ""
        if normalized.endswith("/index.html"):
            return normalized[: -len("index.html")]
        return normalized

    @staticmethod
    def site_root_for_output_path(output_path: str) -> str:
        return "../" * output_path.replace("\\", "/").count("/")
