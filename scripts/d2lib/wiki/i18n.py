from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional, Tuple

from d2lib.repository import D2RepositoryProtocol, resolve_localized_string

MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
D2LIB_DIR = os.path.dirname(MODULE_DIR)
REPO_ROOT = os.path.abspath(os.path.join(D2LIB_DIR, "..", ".."))
DEFAULT_LOCALES_DIR = os.path.join(REPO_ROOT, "data", "wiki_locales")

LOCALE_DISPLAY_NAMES: Dict[str, str] = {
    "enUS": "English",
    "deDE": "Deutsch",
    "esES": "Español (EU)",
    "esMX": "Español (LA)",
    "frFR": "Français",
    "itIT": "Italiano",
    "jaJP": "日本語",
    "koKR": "한국어",
    "plPL": "Polski",
    "ptBR": "Português (BR)",
    "ruRU": "Русский",
    "zhCN": "简体中文",
    "zhTW": "繁體中文",
}

# Mapping of wiki UI key -> (D2R string table key, strip trailing ": %d..." suffix).
D2_UI_STRING_KEYS: Dict[str, Tuple[str, bool]] = {
    "stat.str_req": ("ItemStats1e", True),
    "stat.dex_req": ("ItemStats1f", True),
    "stat.defense": ("ItemStats1h", True),
    "stat.one_hand_damage": ("ItemStats1l", True),
    "stat.two_hand_damage": ("ItemStats1m", True),
    "stat.throw_damage": ("ItemStats1n", True),
    "stat.required_level": ("ItemStats1p", True),
    "stat.level_req": ("ItemStats1p", True),
    "stat.block": ("ItemStats1r", True),
    "nav.items": ("AdvancedItems", False),
    "nav.runewords": ("Runewords", False),
    "nav.sets": ("Sets", False),
    "nav.skills": ("AdvancedPlayerSkills", False),
    "nav.misc": ("materials", False),
    "nav.mercenaries": ("MiniPanelHireinv", False),
    "quality.unique": ("LootFilterUniqueRarity", False),
    "quality.set": ("LootFilterSetRarity", False),
    "quality.magic": ("LootFilterMagicRarity", False),
    "quality.rare": ("LootFilterRareRarity", False),
    "quality.normal": ("LootFilterNormalQuality", False),
    "common.quality": ("LootFilterQualityTitle", False),
    "common.close": ("strClose", False),
    "common.search": ("LobbySearch", False),
    "common.class": ("strClass", False),
    "common.level": ("strchrlvl", False),
    "common.yes": ("VerifyTransaction1", False),
    "common.no": ("VerifyTransaction2", False),
    "common.all": ("LadderClassFilterAll", False),
    "common.none": ("strNone", False),
    "common.filters": ("GameListFilters", False),
    "stat.runes": ("runes", False),
    "stat.set": ("LootFilterSetRarity", False),
    "drops.sets": ("Sets", False),
    "merc.stat.strength": ("strchrstr", False),
    "merc.stat.dexterity": ("strchrdex", False),
    "merc.stat.defense": ("strchrdef", False),
    "merc.stat.fire": ("StrSklTree25", False),
    "merc.stat.cold": ("StrSklTree23", False),
    "merc.stat.lightning": ("StrSklTree24", False),
    "merc.stat.poison": ("StrSklTree17", False),
}

STAT_ROW_I18N_KEYS: Dict[str, str] = {
    "defense": "stat.defense",
    "one_hand_damage": "stat.one_hand_damage",
    "two_hand_damage": "stat.two_hand_damage",
    "throw_damage": "stat.throw_damage",
    "level": "stat.base_level",
    "level_req": "stat.level_req",
    "required_level": "stat.required_level",
    "str_req": "stat.str_req",
    "dex_req": "stat.dex_req",
    "max_sockets": "stat.max_sockets",
    "block": "stat.block",
    "speed": "stat.speed",
    "runes": "stat.runes",
    "base_items": "stat.base_items",
    "base_item": "stat.base_item",
    "item_type": "stat.item_type",
    "set": "stat.set",
    "cost": "stat.cost",
    "inherent": "stat.inherent",
    "auto_prefix": "stat.auto_prefix",
    "superior_bonuses": "stat.superior_bonuses",
}

JS_UI_KEYS: Tuple[str, ...] = (
    "status.modified",
    "status.mod_only",
    "common.no",
    "common.unknown",
    "common.count_of_total",
    "areas.lvl_short",
    "areas.no_monster_pool",
    "areas.no_monster_pool_data",
    "areas.more_monsters",
    "areas.sparkly_chest",
    "areas.sparkly_chest_title",
    "areas.super_chest",
    "areas.super_chest_title",
    "areas.room_singular",
    "areas.room_plural",
    "areas.unknown_rooms",
    "areas.tiles_count",
    "areas.avg_short",
    "areas.density",
    "areas.elite_packs",
    "areas.special_chest",
    "areas.possible_immunities",
    "areas.monster_pool",
    "areas.no_matches",
    "areas.load_error",
    "search.no_matching_entries",
    "runewords.no_matches",
    "skills.visible_count",
    "history.dialog_title",
    "history.loading",
    "history.no_revisions",
    "history.load_error",
    "history.event.current",
    "history.event.changed",
    "history.event.added",
    "history.event.first_recorded",
    "history.event.activation_changed",
    "history.event.removed",
    "history.event.reappeared",
    "history.event.recorded_after_gap",
    "history.event.source_gap",
)


class _SafeFormatDict(dict):
    def __missing__(self, key: str) -> str:
        return "{" + str(key) + "}"


def locale_display_name(locale: str) -> str:
    """Return the native human-readable label for a D2R locale code."""
    clean = str(locale or "").strip() or "enUS"
    return LOCALE_DISPLAY_NAMES.get(clean, clean)


def _strip_stat_label(value: str) -> str:
    clean = str(value or "").strip()
    for sep in (":", "："):
        if sep in clean:
            clean = clean.split(sep, 1)[0].strip()
    return clean


def _load_locale_file(locales_dir: str, locale: str) -> Dict[str, str]:
    path = os.path.join(locales_dir, f"{locale}.json")
    if not os.path.isfile(path):
        return {}
    with open(path, "r", encoding="utf-8-sig") as handle:
        raw = json.load(handle)
    if not isinstance(raw, dict):
        return {}
    return {str(k): str(v) for k, v in raw.items()}


class WikiTranslator:
    """Resolves localized wiki UI chrome strings with D2R key reuse and enUS fallback."""

    def __init__(
        self,
        locale: str = "enUS",
        repo: Optional[D2RepositoryProtocol] = None,
        locales_dir: Optional[str] = None,
        resolved_strings: Optional[Dict[str, str]] = None,
    ):
        self.locale = str(locale or "enUS").strip() or "enUS"
        self.locales_dir = locales_dir or DEFAULT_LOCALES_DIR
        self.fallback_strings: Dict[str, str] = _load_locale_file(self.locales_dir, "enUS")
        self.strings: Dict[str, str] = dict(self.fallback_strings)

        if resolved_strings is not None:
            for key, value in resolved_strings.items():
                self.strings[str(key)] = str(value)
            return

        if self.locale != "enUS":
            locale_overrides = _load_locale_file(self.locales_dir, self.locale)
            self.strings.update(locale_overrides)

        if repo is not None:
            for ui_key, (d2_key, strip_suffix) in D2_UI_STRING_KEYS.items():
                # Keep canonical enUS catalog overrides (e.g. compact "Def"/"Req Lvl") intact.
                if self.locale == "enUS" and ui_key in self.fallback_strings:
                    continue
                localized = resolve_localized_string(repo, d2_key)
                if not localized:
                    continue
                if strip_suffix:
                    localized = _strip_stat_label(localized)
                if localized:
                    self.strings[ui_key] = localized

    def t(self, key: str, **kwargs: Any) -> str:
        template = self.strings.get(key) or self.fallback_strings.get(key) or key
        if not kwargs:
            return template
        return template.format_map(_SafeFormatDict(kwargs))

    def stat_label(self, row: Dict[str, Any]) -> str:
        raw_label = str(row.get("label") or "")
        if not raw_label:
            return ""
        stat_key = str(row.get("key") or "")
        i18n_key = STAT_ROW_I18N_KEYS.get(stat_key)
        if not i18n_key or self.locale == "enUS":
            return raw_label
        return self.t(i18n_key)

    def js_catalog(self, new_label: str = "BKDiablo", old_label: str = "Retail") -> Dict[str, str]:
        catalog: Dict[str, str] = {}
        for key in JS_UI_KEYS:
            value = self.strings.get(key) or self.fallback_strings.get(key) or key
            if key == "status.mod_only" and new_label:
                value = value.format_map(_SafeFormatDict({"new_label": new_label, "old_label": old_label}))
            catalog[key] = value
        return catalog

    def js_json(self, new_label: str = "BKDiablo", old_label: str = "Retail") -> str:
        raw = json.dumps(self.js_catalog(new_label=new_label, old_label=old_label), ensure_ascii=False)
        return raw.replace("</", "<\\/").replace("<!--", "<\\!--")
