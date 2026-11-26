from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Set, Tuple

from d2lib.models import CubeRecipeDTO, CubeRecipeGroupDTO
from d2lib.repository import D2Repository, D2RepositoryProtocol, resolve_localized_string
from d2lib.services.base import _status_for_row
from d2lib.services.item_types import ItemTypeTaxonomy
from d2lib.services.resolver import PropertyResolverService
from d2lib.utils import slugify

_RUNE_CODE_RE = re.compile(r"^r(\d+)$", re.IGNORECASE)
_CORRUPTION_RARITY_LEGACY_RE = re.compile(
    r"^(?P<label>.+?) \((?P<rarity>Crafted|Magic|Rare|Set|Unique)\)$"
)
_CORRUPTION_TARGET_LEGACY_RE = re.compile(r"^(?P<label>.+?) \((?P<rarities>[^)]+)\)$")


class CubeAnalyzerService:
    GROUP_META = {
        "Socketing & Sockets": {
            "id": "socketing",
            "order": 10,
            "action": "Add, clear, or shape sockets",
            "summary": "Socket recipes, unsocketing, and socket-related item setup.",
        },
        "Item Upgrades": {
            "id": "item-upgrades",
            "order": 20,
            "action": "Upgrade item bases or tiers",
            "summary": "Exceptional, elite, ethereal, set, unique, and base upgrade paths.",
        },
        "Classic Crafting": {
            "id": "classic-crafting",
            "order": 30,
            "action": "Craft familiar Blood, Caster, Safety, and Hit Power items",
            "summary": "Classic craft families using magic bases and crafting inputs.",
        },
        "Pierce Amulet Crafting": {
            "id": "pierce-amulets",
            "order": 40,
            "action": "Craft pierce-focused amulets",
            "summary": "Elemental, magic, physical, and poison pierce amulet families.",
        },
        "Ascended Crafting": {
            "id": "ascended-crafting",
            "order": 50,
            "action": "Use ascended gems and endgame components",
            "summary": "Ascended gem recipes and high-tier crafting conversions.",
        },
        "Corruption Recipes": {
            "id": "corruption",
            "order": 60,
            "action": "Corrupt or modify items",
            "summary": "Risk/reward item mutation recipes and corruption support recipes.",
        },
        "Rune Transmutation": {
            "id": "runes",
            "order": 70,
            "action": "Upgrade or convert runes",
            "summary": "Rune upgrades and rune-related cube conversions.",
        },
        "Material Upgrades & Conversions": {
            "id": "materials",
            "order": 75,
            "action": "Upgrade gems, essences, and material stacks",
            "summary": "Gem tiers, essence conversions, bricks, sigils, and other material ladders.",
        },
        "Crafting Tablets": {
            "id": "tablets",
            "order": 80,
            "action": "Create or convert crafting tablets",
            "summary": "Tablet recipes and tablet-driven crafting inputs.",
        },
        "Item Reforging & Cosmetics": {
            "id": "reforging",
            "order": 85,
            "action": "Change item state, color, or presentation",
            "summary": "Ethereal, superior, inferior, color, transmogrify, and generated base-item transforms.",
        },
        "Repair & Recharge": {
            "id": "repair",
            "order": 90,
            "action": "Repair, recharge, or restore items",
            "summary": "Durability, quantity, and charge restoration recipes.",
        },
        "Charm, Jewel & Reward Recipes": {
            "id": "charms-jewels-rewards",
            "order": 95,
            "action": "Create charms, jewels, and named rewards",
            "summary": "Charm setup, unique jewels, and reward item conversions.",
        },
        "Stacking & Utility": {
            "id": "stacking",
            "order": 100,
            "action": "Stack, unstack, or convert supplies",
            "summary": "Convenience recipes for stackables, consumables, and utility items.",
        },
        "Portals & Quest Recipes": {
            "id": "portals-quests",
            "order": 110,
            "action": "Open content or complete progression combines",
            "summary": "Portal, quest, cow level, and access-related cube recipes.",
        },
        "General Recipes": {
            "id": "general",
            "order": 800,
            "action": "Review remaining enabled recipes",
            "summary": "Enabled recipes that need more specific player-facing classification.",
        },
        "Removed Baseline Recipes": {
            "id": "removed-retail",
            "order": 900,
            "action": "See baseline recipes not present in BK",
            "summary": "Recipes from the selected comparison baseline that are absent from the BK enabled recipe set.",
        },
    }

    QUALIFIER_ALIASES: Dict[str, str] = {
        "hi": "hiq",
        "bas": "nor",
        "ora": "crf",
    }

    QUALIFIER_STRING_KEYS: Dict[str, Tuple[str, str]] = {
        "low": ("LootFilterInferiorRarity", "Inferior"),
        "nor": ("LootFilterNormalQuality", "Normal"),
        "exc": ("LootFilterExceptionalQuality", "Exceptional"),
        "eli": ("LootFilterEliteQuality", "Elite"),
        "hiq": ("LootFilterSuperiorRarity", "Superior"),
        "mag": ("LootFilterMagicRarity", "Magic"),
        "rar": ("LootFilterRareRarity", "Rare"),
        "set": ("LootFilterSetRarity", "Set"),
        "uni": ("LootFilterUniqueRarity", "Unique"),
        "crf": ("LootFilterCraftedRarity", "Crafted"),
        "tmp": ("LootFilterTemperedRarity", "Tempered"),
    }

    QUALITY_ORDER: Tuple[str, ...] = (
        "low", "nor", "hiq", "exc", "eli", "mag", "rar", "set", "uni", "crf", "tmp"
    )
    CORRUPTION_RARITY_ORDER: Tuple[str, ...] = ("crf", "mag", "rar", "set", "uni")

    def __init__(self, repo: D2RepositoryProtocol, retail_repo: Optional[D2RepositoryProtocol] = None):
        self.repo = repo
        self.retail_repo = retail_repo
        self.resolver = PropertyResolverService(repo)
        self.armor = {row["code"]: row for row in repo.get_excel_table("armor") if row.get("code")}
        self.weapons = {row["code"]: row for row in repo.get_excel_table("weapons") if row.get("code")}
        self.misc = {row["code"]: row for row in repo.get_excel_table("misc") if row.get("code")}
        self.item_types = {row["Code"]: row for row in repo.get_excel_table("itemtypes") if row.get("Code")}
        self.taxonomy = ItemTypeTaxonomy(repo)

        self._items_by_code_ci: Dict[str, Dict[str, str]] = {}
        for table_map in (self.armor, self.weapons, self.misc):
            for code, row in table_map.items():
                self._items_by_code_ci.setdefault(code.casefold(), row)

        self._item_types_by_code_ci: Dict[str, str] = {
            code.casefold(): code for code in self.item_types
        }

        self.unique_items_by_name: Dict[str, Dict[str, str]] = {}
        for row in repo.get_excel_table("uniqueitems"):
            idx = row.get("index", "").strip()
            if not idx:
                continue
            self.unique_items_by_name.setdefault(idx.casefold(), row)
            localized = resolve_localized_string(repo, idx)
            if localized:
                self.unique_items_by_name.setdefault(localized.casefold(), row)

        self.set_items_by_name: Dict[str, Dict[str, str]] = {}
        for row in repo.get_excel_table("setitems"):
            idx = row.get("index", "").strip()
            if not idx:
                continue
            self.set_items_by_name.setdefault(idx.casefold(), row)
            localized = resolve_localized_string(repo, idx)
            if localized:
                self.set_items_by_name.setdefault(localized.casefold(), row)

        self._inferred_type_parents: Dict[str, List[str]] = self._infer_type2_parents()

        self.retail_recipe_rows = (
            {
                row.get("description", "").strip().lower(): row
                for row in retail_repo.get_excel_table("cubemain")
                if row.get("description") and self._is_enabled_recipe_row(row)
            }
            if retail_repo
            else {}
        )

        # Prefixes and Suffixes use row index as ID
        prefix_data = repo.get_excel_table("magicprefix")
        self.prefixes = {str(i): row for i, row in enumerate(prefix_data)}
        self._pierce_prefix_by_mod: Dict[str, str] = {}
        self._pierce_prefix_to_mod: Dict[str, str] = {}
        self._pierce_mods: Set[str] = set()
        for row in prefix_data:
            raw_name = row.get("Name", "").strip()
            for idx in range(1, 4):
                mod_code = row.get(f"mod{idx}code", "").strip().lower()
                if not mod_code.startswith("pierce-"):
                    continue
                self._pierce_mods.add(mod_code)
                if raw_name:
                    self._pierce_prefix_by_mod.setdefault(mod_code, raw_name)
                    self._pierce_prefix_to_mod.setdefault(raw_name.casefold(), mod_code)

        suffix_data = repo.get_excel_table("magicsuffix")
        self.suffixes = {str(i): row for i, row in enumerate(suffix_data)}

        self._crafting_catalyst_codes: Set[str] = self._discover_crafting_catalysts()
        self._condensed_recipe_ids: Set[str] = set()

    def _infer_type2_parents(self) -> Dict[str, List[str]]:
        """Infers parent item types for `type2` tags that lack `Equiv1`/`Equiv2` in `itemtypes.txt`."""
        type2_chains: Dict[str, List[Tuple[str, List[str]]]] = {}
        for table_map in (self.weapons, self.armor, self.misc):
            for row in table_map.values():
                t1 = row.get("type", "").strip()
                t2 = row.get("type2", "").strip()
                if not t1 or not t2 or t2 not in self.item_types:
                    continue
                t2_row = self.item_types[t2]
                if t2_row.get("Equiv1", "").strip() or t2_row.get("Equiv2", "").strip():
                    continue
                if t2 in {"weap", "armo", "misc", "any"}:
                    continue
                type2_chains.setdefault(t2, []).append((t1, self.taxonomy.chain(t1)))

        inferred: Dict[str, List[str]] = {}
        for t2, entries in type2_chains.items():
            common: Optional[Set[str]] = None
            for t1, chain in entries:
                ancestors = {code for code in chain if code not in {t1, t2}}
                common = ancestors if common is None else (common & ancestors)
            if not common:
                continue
            sample_order = entries[0][1]
            inferred[t2] = [code for code in sample_order if code in common]
        return inferred

    def _discover_crafting_catalysts(self) -> Set[str]:
        """Discovers catalyst item codes used as crafting inputs (e.g. tablets)."""
        catalysts: Set[str] = set()
        for row in self.repo.get_excel_table("cubemain"):
            if not self._is_enabled_recipe_row(row):
                continue
            if not self._is_craft_row(row):
                continue
            in2 = row.get("input 2", "").strip()
            if not in2 or in2 == "0":
                continue
            base_code = self.parse_token(in2)[0].lower()
            if not base_code or self._is_jewel_code(base_code) or self._is_gem_code(base_code) or self._is_rune_code(base_code):
                continue
            catalysts.add(base_code)
        return catalysts

    @classmethod
    def canonical_qualifier(cls, code: str) -> str:
        clean = (code or "").strip().lower()
        return cls.QUALIFIER_ALIASES.get(clean, clean)

    def qualifier_label(self, code: str) -> str:
        canonical = self.canonical_qualifier(code)
        entry = self.QUALIFIER_STRING_KEYS.get(canonical)
        if not entry:
            return code
        string_key, fallback = entry
        return resolve_localized_string(self.repo, string_key) or fallback

    def state_label(self, code: str, value: str = "") -> str:
        clean = (code or "").strip().lower()
        if clean == "eth":
            raw_eth = resolve_localized_string(self.repo, "strethereal")
            if raw_eth:
                short = raw_eth.split(" (", 1)[0].strip()
                if short:
                    return short.lower()
            return "ethereal"
        if clean == "noe":
            eth_lbl = self.state_label("eth")
            return f"non-{eth_lbl}" if eth_lbl.isascii() else "non-ethereal"
        if clean == "nos":
            return "unsocketed"
        if clean == "sock":
            tmpl = resolve_localized_string(self.repo, "Socketable")
            if value:
                if tmpl:
                    return re.sub(r"%(?:i|d)", value, tmpl)
                return f"Socketed ({value})"
            if tmpl:
                stripped = re.sub(r"\s*\([^)]*%(?:i|d)[^)]*\)", "", tmpl).strip()
                if stripped:
                    return stripped.lower()
            return "socketed"
        action_labels = {
            "uns": "clear sockets",
            "rem": "extract socketed items",
            "rep": "repaired",
            "rch": "recharged",
            "mod": "keeps properties",
            "upg": "upgradable",
        }
        return action_labels.get(clean, clean)

    @staticmethod
    def parse_token(token: str) -> Tuple[str, List[str], str]:
        """Parses a cubemain input/output token into (base_code, flags, qty)."""
        if not token:
            return "", [], ""
        clean = token.strip().strip('"').strip()
        if not clean or clean == "0":
            return "", [], ""
        parts = [part.strip() for part in clean.split(",") if part.strip()]
        if not parts:
            return "", [], ""
        base_code = parts[0]
        flags: List[str] = []
        qty = ""
        for part in parts[1:]:
            lower = part.lower()
            if lower.startswith("qty="):
                qty = part.split("=", 1)[1].strip()
            else:
                flags.append(part)
        return base_code, flags, qty

    def _find_base_item(self, code: str) -> Optional[Dict[str, str]]:
        clean = (code or "").strip()
        if not clean:
            return None
        return (
            self.armor.get(clean)
            or self.weapons.get(clean)
            or self.misc.get(clean)
            or self._items_by_code_ci.get(clean.casefold())
        )

    def _find_named_item(self, code: str) -> Optional[Dict[str, str]]:
        clean = (code or "").strip().casefold()
        if not clean:
            return None
        return self.unique_items_by_name.get(clean) or self.set_items_by_name.get(clean)

    def get_item_name(self, code: str) -> str:
        if not code:
            return ""
        code = code.strip()
        code_lower = code.lower()
        if code_lower == "usetype":
            return "Input Item Type"
        if code_lower == "useitem":
            return "Input Item"
        if code_lower == "any":
            return "Any Item"

        item = self._find_base_item(code)
        if item:
            name_key = item.get("namestr", "").strip() or item.get("name", "").strip()
            localized = resolve_localized_string(self.repo, name_key)
            if localized:
                return localized
            fallback_name = item.get("name", "").strip()
            return self.repo.get_string(name_key) if not fallback_name else fallback_name

        type_code = code if code in self.item_types else self._item_types_by_code_ci.get(code_lower, "")
        if type_code:
            type_row = self.item_types[type_code]
            ui_cat = type_row.get("UICategory", "").strip()
            raw_item_type = type_row.get("ItemType", "").strip()
            # Prefer localized misc UICategory (e.g. poti -> Potions) for recipe type labels.
            if type_row.get("Equiv1", "").strip() == "misc" and ui_cat:
                resolved = (
                    resolve_localized_string(self.repo, ui_cat)
                    or resolve_localized_string(self.repo, raw_item_type)
                    or self.taxonomy.label(type_code)
                )
                return resolved or code
            return self.taxonomy.label(type_code) or code

        named_row = self._find_named_item(code)
        if named_row:
            raw_index = named_row.get("index", "").strip()
            return resolve_localized_string(self.repo, raw_index) or raw_index or code

        return resolve_localized_string(self.repo, code) or code

    def item_type_chain_for_token(self, token_or_code: str) -> List[str]:
        base_code = self.parse_token(token_or_code)[0] or (token_or_code or "").strip()
        if not base_code:
            return []
        base_lower = base_code.lower()
        if base_lower in {"usetype", "useitem"}:
            return []
        if base_lower == "any":
            return ["any"]

        type_code = base_code if base_code in self.item_types else self._item_types_by_code_ci.get(base_lower, "")
        if type_code:
            return [type_code] + self._item_type_ancestors(type_code)

        item = self._find_base_item(base_code)
        if not item:
            named_row = self._find_named_item(base_code)
            if named_row:
                item_code = (named_row.get("code") or named_row.get("item") or "").strip()
                item = self._find_base_item(item_code)
        if not item:
            return []

        chain: List[str] = []
        seen: Set[str] = set()
        for col in ("type", "type2"):
            t_code = item.get(col, "").strip()
            if not t_code:
                continue
            for node in [t_code] + self._item_type_ancestors(t_code):
                if node not in seen:
                    seen.add(node)
                    chain.append(node)
        return chain

    def has_item_type(self, token_or_code: str, type_code: str) -> bool:
        target = (type_code or "").strip().lower()
        if not target:
            return False
        return any(node.lower() == target for node in self.item_type_chain_for_token(token_or_code))

    def _is_gem_code(self, code: str) -> bool:
        return self.has_item_type(code, "gem")

    def _is_rune_code(self, code: str) -> bool:
        clean = (code or "").strip()
        return self.has_item_type(clean, "rune") or bool(_RUNE_CODE_RE.match(clean))

    def _is_jewel_code(self, code: str) -> bool:
        clean = (code or "").strip().lower()
        return self.has_item_type(clean, "jewl") or clean == "jew"

    def _rune_tier(self, code: str) -> int:
        match = _RUNE_CODE_RE.match((code or "").strip())
        return int(match.group(1)) if match else 0

    def _format_flag(self, flag: str) -> str:
        lower = (flag or "").strip().lower()
        if not lower:
            return ""
        canonical = self.canonical_qualifier(lower)
        if canonical in self.QUALIFIER_STRING_KEYS:
            return self.qualifier_label(canonical)
        if lower.startswith("sock="):
            return self.state_label("sock", lower.split("=", 1)[1].strip())
        if lower.startswith("lvl="):
            return f"Lvl: {lower.split('=', 1)[1].strip()}"
        if lower.startswith("pre="):
            val = lower.split("=", 1)[1].strip()
            pre = self.prefixes.get(val)
            raw_pre = pre.get("Name", "") if pre else val
            pre_name = (resolve_localized_string(self.repo, raw_pre) or raw_pre) if pre else val
            return f"Prefix: {pre_name} ({val})"
        if lower.startswith("suf="):
            val = lower.split("=", 1)[1].strip()
            suf = self.suffixes.get(val)
            raw_suf = suf.get("Name", "") if suf else val
            suf_name = (resolve_localized_string(self.repo, raw_suf) or raw_suf) if suf else val
            return f"Suffix: {suf_name} ({val})"
        if lower in {"eth", "noe", "nos", "sock", "uns", "rem", "rep", "rch", "mod", "upg"}:
            return self.state_label(lower)
        return lower

    def resolve_token(self, token: str) -> str:
        base_code, flags, qty = self.parse_token(token)
        if not base_code:
            return ""
        name = self.get_item_name(base_code)
        mods = [self._format_flag(flag) for flag in flags if self._format_flag(flag)]
        res = f"{name} ({', '.join(mods)})" if mods else name
        return f"{res} (Qty: {qty})" if qty else res

    def resolve_output(self, out: str, mod_str: str = "", mod_val: str = "") -> str:
        if not out:
            return ""
        res = self.resolve_token(out)
        extra_mods: List[str] = []
        if mod_str:
            for raw_part in mod_str.split(","):
                lower = raw_part.strip().lower()
                if not lower:
                    continue
                canonical = self.canonical_qualifier(lower)
                if canonical in self.QUALIFIER_STRING_KEYS:
                    extra_mods.append(self.qualifier_label(canonical))
                elif lower == "pre":
                    pre = self.prefixes.get(mod_val)
                    raw_pre = pre.get("Name", "") if pre else mod_val
                    pre_name = (resolve_localized_string(self.repo, raw_pre) or raw_pre) if pre else mod_val
                    extra_mods.append(f"Prefix: {pre_name} ({mod_val})")
                elif lower == "suf":
                    suf = self.suffixes.get(mod_val)
                    raw_suf = suf.get("Name", "") if suf else mod_val
                    suf_name = (resolve_localized_string(self.repo, raw_suf) or raw_suf) if suf else mod_val
                    extra_mods.append(f"Suffix: {suf_name} ({mod_val})")
                else:
                    extra_mods.append(self.state_label(lower) if lower in {"eth", "noe", "nos", "sock"} else lower)
        if extra_mods:
            res += f" [Extra: {', '.join(extra_mods)}]"
        return res

    def analyze_recipe(self, row: Dict[str, str], status: Optional[str] = None) -> CubeRecipeDTO:
        desc = row.get("description", "Unknown Recipe").strip()
        enabled = row.get("enabled", "1").strip() == "1"
        actual_inputs = []
        for i in range(1, 8):
            val = row.get(f"input {i}", "").strip()
            if val and val != "0":
                actual_inputs.append(self.resolve_token(val))
        outputs = []
        output_slots = [
            ("output", "mod 1", "mod 1 param"),
            ("output 2", "mod 2", "mod 2 param"),
            ("output 3", "mod 3", "mod 3 param"),
            ("output b", "b mod 1", "b mod 1 param"),
            ("output c", "c mod 1", "c mod 1 param"),
        ]
        for output_column, mod_column, mod_param_column in output_slots:
            out = row.get(output_column, "").strip()
            if out and out != "0":
                mod_str = row.get(mod_column, "").strip()
                mod_val = row.get(mod_param_column, "").strip()
                outputs.append(self.resolve_output(out, mod_str, mod_val))
        if status is None:
            status = _status_for_row(desc.lower(), row, self.retail_recipe_rows) if self.retail_repo else "unchanged"
        return {
            "id": desc,
            "description": desc,
            "enabled": enabled,
            "status": status,
            "inputs": actual_inputs,
            "outputs": outputs,
            "raw_row": row,
        }

    def analyze_all_recipes(self) -> List[CubeRecipeGroupDTO]:
        all_recipes = self.analyze_raw_recipes(include_removed=True)
        groups: Dict[str, List[CubeRecipeDTO]] = {}

        for r in all_recipes:
            group_name = self._recipe_group_name(r)
            groups.setdefault(group_name, []).append(r)

        return [
            {
                "id": meta["id"],
                "name": name,
                "summary": meta["summary"],
                "action": meta["action"],
                "order": meta["order"],
                "status_counts": self._recipe_status_counts(recipes),
                "corruption_summaries": self._corruption_summaries(recipes) if name == "Corruption Recipes" else [],
                "recipes": sorted(self._display_recipes(name, recipes), key=self._recipe_sort_key),
            }
            for name, recipes in sorted(
                groups.items(),
                key=lambda entry: (self.GROUP_META.get(entry[0], self.GROUP_META["General Recipes"])["order"], entry[0]),
            )
            for meta in [self.GROUP_META.get(name, self.GROUP_META["General Recipes"])]
        ]

    def _display_recipes(self, group_name: str, recipes: List[CubeRecipeDTO]) -> List[CubeRecipeDTO]:
        if group_name in {"Classic Crafting", "Ascended Crafting"}:
            return self._condense_classic_crafting(recipes)
        if group_name == "Item Upgrades":
            return self._condense_item_upgrades(recipes)
        if group_name in {"Socketing & Sockets", "Item Reforging & Cosmetics"}:
            return self._condense_socketing_recipes(recipes)
        return recipes

    def _condense_classic_crafting(self, recipes: List[CubeRecipeDTO]) -> List[CubeRecipeDTO]:
        grouped: Dict[Tuple[Any, ...], List[CubeRecipeDTO]] = {}
        passthrough: List[CubeRecipeDTO] = []

        for recipe in recipes:
            key = self._classic_craft_key(recipe)
            if key is None:
                passthrough.append(recipe)
                continue
            grouped.setdefault(key, []).append(recipe)

        condensed = passthrough[:]
        for rows in grouped.values():
            condensed.append(self._classic_craft_display_recipe(rows))
        return condensed

    def _classic_craft_key(self, recipe: CubeRecipeDTO) -> Optional[Tuple[Any, ...]]:
        raw = recipe.get("raw_row", {})
        if not self._is_craft_row(raw):
            return None
        output = raw.get("output", "").strip()

        modifiers = tuple(
            (
                raw.get(f"mod {index}", "").strip(),
                raw.get(f"mod {index} param", "").strip(),
                raw.get(f"mod {index} min", "").strip(),
                raw.get(f"mod {index} max", "").strip(),
                raw.get(f"mod {index} chance", "").strip(),
            )
            for index in range(1, 6)
            if raw.get(f"mod {index}", "").strip()
        )
        if not modifiers:
            return None

        extra_inputs = tuple(
            raw.get(f"input {index}", "").strip()
            for index in range(2, 8)
            if raw.get(f"input {index}", "").strip() and raw.get(f"input {index}", "").strip() != "0"
        )
        return (recipe.get("status", "unchanged"), output, extra_inputs, modifiers)

    def _classic_craft_display_recipe(self, rows: List[CubeRecipeDTO]) -> CubeRecipeDTO:
        first = rows[0]
        raw = first.get("raw_row", {})
        family = self._craft_family_name(raw.get("input 2", ""), first.get("description", ""), raw)
        base_label = self._classic_craft_base_label(rows)
        extra_inputs = self._classic_craft_extra_inputs(raw)
        result = self._classic_craft_result(raw)
        modifiers = self._resolve_output_modifiers(raw)

        inputs = [base_label] + [self.resolve_token(token) for token in extra_inputs]
        outputs = [result]
        if modifiers:
            outputs.append("Fixed properties: " + "; ".join(modifiers))

        base_names = self._classic_craft_base_names(rows)
        display_description = f"{family} {base_names[0]} Craft" if len(base_names) == 1 else f"{family} Craft"
        self._condensed_recipe_ids.add(display_description)

        return {
            "id": display_description,
            "description": display_description,
            "enabled": True,
            "status": first.get("status", "unchanged"),
            "inputs": inputs,
            "outputs": outputs,
            "raw_row": raw,
        }

    def _craft_family_name(
        self,
        tablet_code: str,
        description: str = "",
        raw: Optional[Dict[str, str]] = None,
    ) -> str:
        # Classify craft family from mod columns first so multi-mod recipes (e.g. Ascended Safety)
        # do not depend on English author comments or gem item existence.
        if raw:
            mods = self._row_mod_codes(raw)
            if "lifesteal" in mods:
                return "Blood"
            if mods & {"regen-mana", "mana-kill", "allskills", "cast1", "mana%"}:
                return "Caster"
            if mods & {"red-dmg", "red-mag", "red-dmg%", "res-curse"}:
                return "Safety"
            if "gethit-skill" in mods:
                return "Hit Power"

        code = self.parse_token(tablet_code)[0] or tablet_code.strip()
        item = self._find_base_item(code)
        name = (
            resolve_localized_string(self.repo, item.get("namestr", "") or item.get("name", ""))
            or (item.get("name", "").strip() if item else "")
            or self.get_item_name(code)
        )
        for suffix in (" Crafting Tablet", " Tablet"):
            if name.endswith(suffix):
                return name[: -len(suffix)]
        return name or "Crafting"

    def _classic_craft_base_label(self, rows: List[CubeRecipeDTO]) -> str:
        base_names = self._classic_craft_base_names(rows)
        quality_names = self._quality_names_for_rows(rows)
        eth_states = self._state_labels_for_rows(rows, include_nos=False)

        quality = " ".join(quality_names) if quality_names else ""
        if len(base_names) == 1:
            label = " ".join(part for part in (quality, base_names[0]) if part)
        else:
            label = " ".join(part for part in (quality, "Items") if part)
            label += f": {', '.join(base_names)}"

        if len(eth_states) == 1:
            label += f" ({eth_states[0]})"
        return label

    def _classic_craft_base_names(self, rows: List[CubeRecipeDTO]) -> List[str]:
        return self._base_names_for_rows(rows)

    @staticmethod
    def _classic_craft_extra_inputs(raw: Dict[str, str]) -> List[str]:
        return [
            raw.get(f"input {index}", "").strip()
            for index in range(2, 8)
            if raw.get(f"input {index}", "").strip() and raw.get(f"input {index}", "").strip() != "0"
        ]

    def _classic_craft_result(self, raw: Dict[str, str]) -> str:
        output = raw.get("output", "").strip()
        if self._is_craft_row(raw):
            return self.resolve_output(output)
        return self.resolve_output(output, raw.get("mod 1", "").strip(), raw.get("mod 1 param", "").strip())

    def _resolve_output_modifiers(self, raw: Dict[str, str]) -> List[str]:
        modifiers: List[str] = []
        for index in range(1, 6):
            code = raw.get(f"mod {index}", "").strip()
            if not code:
                continue
            resolved = self.resolver.resolve_property(
                code,
                raw.get(f"mod {index} param", ""),
                raw.get(f"mod {index} min", ""),
                raw.get(f"mod {index} max", ""),
            )
            text = resolved.get("resolved_text", "").strip()
            if text and not text.startswith("Unknown property (") and text not in modifiers:
                modifiers.append(text)
        return modifiers

    def _condense_item_upgrades(self, recipes: List[CubeRecipeDTO]) -> List[CubeRecipeDTO]:
        grouped: Dict[Tuple[Any, ...], List[CubeRecipeDTO]] = {}
        passthrough: List[CubeRecipeDTO] = []

        for recipe in recipes:
            key = self._item_upgrade_key(recipe)
            if key is None:
                passthrough.append(recipe)
                continue
            grouped.setdefault(key, []).append(recipe)

        condensed = passthrough[:]
        for rows in grouped.values():
            condensed.append(self._item_upgrade_display_recipe(rows))
        return condensed

    def _item_upgrade_key(self, recipe: CubeRecipeDTO) -> Optional[Tuple[Any, ...]]:
        raw = recipe.get("raw_row", {})
        base_out, out_flags, _ = self.parse_token(raw.get("output", ""))
        out_flag_set = {self.canonical_qualifier(f) for f in out_flags}
        if base_out.lower() != "useitem" or not (out_flag_set & {"exc", "eli"}):
            return None

        in1_flags = {self.canonical_qualifier(f) for f in self.parse_token(raw.get("input 1", ""))[1]}
        if not (in1_flags & {"nor", "exc"}):
            return None

        extra_inputs = tuple(self._classic_craft_extra_inputs(raw))
        modifiers = tuple(
            raw.get(f"mod {index}", "").strip()
            for index in range(1, 6)
            if raw.get(f"mod {index}", "").strip()
        )
        return (recipe.get("status", "unchanged"), raw.get("output", "").strip().lower(), extra_inputs, modifiers)

    def _item_upgrade_display_recipe(self, rows: List[CubeRecipeDTO]) -> CubeRecipeDTO:
        first = rows[0]
        raw = first.get("raw_row", {})
        out_flags = {self.canonical_qualifier(f) for f in self.parse_token(raw.get("output", ""))[1]}
        is_exc_upgrade = "exc" in out_flags
        from_tier = self.qualifier_label("nor" if is_exc_upgrade else "exc")
        to_tier = self.qualifier_label("exc" if is_exc_upgrade else "eli")
        qualities = self._quality_names_for_rows(rows, exclude={"nor", "exc", "eli"})
        bases = self._display_base_names(self._base_names_for_rows(rows))
        quality_label = self._join_labels(qualities, slash=True)
        base_label = self._join_labels(bases, connector="or")
        subject = " ".join(part for part in (from_tier, quality_label, base_label) if part)

        extra_inputs = [self.resolve_token(token) for token in self._classic_craft_extra_inputs(raw)]
        display_id = f"{from_tier} -> {to_tier} {quality_label} ({base_label})".strip()
        self._condensed_recipe_ids.add(display_id)

        return {
            "id": display_id,
            "description": display_id,
            "enabled": True,
            "status": first.get("status", "unchanged"),
            "inputs": [subject] + extra_inputs,
            "outputs": [f"{to_tier} ({self.get_item_name('useitem')})"],
            "raw_row": raw,
        }

    def _condense_socketing_recipes(self, recipes: List[CubeRecipeDTO]) -> List[CubeRecipeDTO]:
        grouped: Dict[Tuple[Any, ...], List[CubeRecipeDTO]] = {}
        passthrough: List[CubeRecipeDTO] = []

        for recipe in recipes:
            key = self._socket_reforge_key(recipe)
            if key is None:
                passthrough.append(recipe)
                continue
            grouped.setdefault(key, []).append(recipe)

        condensed = passthrough[:]
        for rows in grouped.values():
            condensed.append(self._socket_reforge_display_recipe(rows))
        return condensed

    def _socket_reforge_key(self, recipe: CubeRecipeDTO) -> Optional[Tuple[Any, ...]]:
        raw = recipe.get("raw_row", {})
        if raw.get("output", "").strip().lower() != "useitem":
            return None
        if raw.get("mod 1", "").strip().lower() != "sock":
            return None
        inputs = self._row_inputs(raw)
        if len(inputs) != 2:
            return None
        in1_base = self.parse_token(inputs[0])[0]
        in2_base = self.parse_token(inputs[1])[0]
        if not in1_base or not in2_base:
            return None
        return (
            recipe.get("status", "unchanged"),
            raw.get("output", "").strip().lower(),
            raw.get("mod 1", "").strip().lower(),
            in2_base.lower(),
            in1_base.lower(),
        )

    def _socket_reforge_display_recipe(self, rows: List[CubeRecipeDTO]) -> CubeRecipeDTO:
        first = rows[0]
        raw = first.get("raw_row", {})
        bases = self._display_base_names(self._base_names_for_rows(rows))
        qualities = self._quality_names_for_rows(rows)
        state_labels = self._state_labels_for_rows(rows)
        base_label = self._join_labels(bases, connector="or")
        quality_label = self._join_labels(qualities, slash=True)
        state_suffix = f" ({', '.join(state_labels)})" if state_labels else ""
        item_label = " ".join(part for part in (quality_label, base_label) if part) + state_suffix

        s_min = raw.get("mod 1 min", "").strip()
        s_max = raw.get("mod 1 max", "").strip()
        sock_range = s_min if s_min and s_min == s_max else (f"{s_min}-{s_max}" if s_min and s_max else (s_min or s_max))
        sock_lbl = self.state_label("sock", sock_range)
        catalyst_lbl = self.resolve_token(raw.get("input 2", ""))
        display_id = f"{sock_lbl}: {base_label} (+ {catalyst_lbl})" if base_label else sock_lbl
        self._condensed_recipe_ids.add(display_id)

        return {
            "id": display_id,
            "description": display_id,
            "enabled": True,
            "status": first.get("status", "unchanged"),
            "inputs": [item_label, catalyst_lbl],
            "outputs": [f"{self.get_item_name('useitem')} ({sock_lbl})"],
            "raw_row": raw,
        }

    @staticmethod
    def _raw_token_parts(token: str) -> List[str]:
        return [part.strip().lower() for part in token.strip().strip('"').split(",") if part.strip()]

    def _base_names_for_rows(self, rows: List[CubeRecipeDTO]) -> List[str]:
        names: List[str] = []
        for recipe in rows:
            base_code = self.parse_token(recipe.get("raw_row", {}).get("input 1", ""))[0]
            if not base_code:
                continue
            name = self.get_item_name(base_code)
            if name and name not in names:
                names.append(name)
        return names

    def _quality_names_for_rows(self, rows: List[CubeRecipeDTO], exclude: Optional[Set[str]] = None) -> List[str]:
        seen: Set[str] = set()
        excluded = exclude or set()
        for recipe in rows:
            _base, flags, _qty = self.parse_token(recipe.get("raw_row", {}).get("input 1", ""))
            for flag in flags:
                canonical = self.canonical_qualifier(flag)
                if canonical in self.QUALIFIER_STRING_KEYS and canonical not in excluded:
                    seen.add(canonical)
        return [self.qualifier_label(key) for key in self.QUALITY_ORDER if key in seen]

    def _state_labels_for_rows(self, rows: List[CubeRecipeDTO], include_nos: bool = True) -> List[str]:
        state_keys = ("noe", "eth", "nos") if include_nos else ("noe", "eth")
        seen: Set[str] = set()
        for recipe in rows:
            _base, flags, _qty = self.parse_token(recipe.get("raw_row", {}).get("input 1", ""))
            for flag in flags:
                lower = flag.strip().lower()
                if lower in state_keys:
                    seen.add(lower)
        return [self.state_label(key) for key in state_keys if key in seen]

    def _display_base_names(self, names: List[str]) -> List[str]:
        armor_fallback = resolve_localized_string(self.repo, "armor") or "Armor"
        shield_fallback = resolve_localized_string(self.repo, "shield") or "Shield"
        replacements = {
            "Any Armor": armor_fallback,
            "Any Shield": shield_fallback,
        }
        return [replacements.get(name, name) for name in names]

    @staticmethod
    def _join_labels(labels: List[str], connector: str = "and", slash: bool = False) -> str:
        if not labels:
            return ""
        if slash:
            return "/".join(labels)
        if len(labels) == 1:
            return labels[0]
        return f"{', '.join(labels[:-1])} {connector} {labels[-1]}"

    @staticmethod
    def _row_inputs(raw: Dict[str, str]) -> List[str]:
        return [
            raw.get(f"input {i}", "").strip()
            for i in range(1, 8)
            if raw.get(f"input {i}", "").strip() and raw.get(f"input {i}", "").strip() != "0"
        ]

    @staticmethod
    def _row_outputs(raw: Dict[str, str]) -> List[str]:
        cols = ("output", "output 2", "output 3", "output b", "output c")
        return [raw.get(col, "").strip() for col in cols if raw.get(col, "").strip() and raw.get(col, "").strip() != "0"]

    @staticmethod
    def _row_mods(raw: Dict[str, str]) -> List[Tuple[str, str, str, str]]:
        return [
            (
                raw.get(f"mod {i}", "").strip(),
                raw.get(f"mod {i} param", "").strip(),
                raw.get(f"mod {i} min", "").strip(),
                raw.get(f"mod {i} max", "").strip(),
            )
            for i in range(1, 6)
            if raw.get(f"mod {i}", "").strip()
        ]

    @classmethod
    def _row_mod_codes(cls, raw: Dict[str, str]) -> Set[str]:
        return {code.lower() for code, _, _, _ in cls._row_mods(raw)}

    def _is_brick_corruption_row(self, raw: Dict[str, str]) -> bool:
        outputs = self._row_outputs(raw)
        if not outputs:
            return False
        if any(self.parse_token(out)[0].lower() == "brk" for out in outputs):
            return True
        if self._to_int(raw.get("value")) > 0:
            base_out, out_flags, _ = self.parse_token(outputs[0])
            if base_out.lower() == "usetype" and len(outputs) > 1 and any(self.canonical_qualifier(f) in {"rar", "mag"} for f in out_flags):
                return True
        return False

    def _is_corruption_row(self, raw: Dict[str, str]) -> bool:
        mod_codes = self._row_mod_codes(raw)
        if any(code.startswith("corruption") for code in mod_codes):
            return True
        return self._to_int(raw.get("value")) > 0 and self._is_brick_corruption_row(raw)

    def _is_socketing_row(self, raw: Dict[str, str]) -> bool:
        if "sock" in self._row_mod_codes(raw):
            return True
        for out in self._row_outputs(raw):
            _, flags, _ = self.parse_token(out)
            lower_flags = {f.split("=", 1)[0].strip().lower() for f in flags}
            if lower_flags & {"sock", "uns", "rem"}:
                return True
        return False

    def _is_craft_row(self, raw: Dict[str, str]) -> bool:
        out = raw.get("output", "").strip().strip('"').lower()
        return out in {"usetype,crf", "usetype,ora"}

    def _craft_source_for_row(self, raw: Dict[str, str]) -> str:
        extra_inputs = self._classic_craft_extra_inputs(raw)
        extra_bases = [self.parse_token(tok)[0] for tok in extra_inputs if self.parse_token(tok)[0]]
        for code in extra_bases:
            item = self._find_base_item(code)
            level_req = self._to_int(item.get("levelreq")) if item else 0
            if self._is_gem_code(code) and level_req >= 50:
                return "Ascended"
            if self._is_rune_code(code) and (level_req >= 37 or self._rune_tier(code) >= 17):
                return "Ascended"
        has_jewel = any(self._is_jewel_code(code) for code in extra_bases)
        if not has_jewel and extra_bases:
            first_extra = extra_bases[0]
            if not self._is_gem_code(first_extra) and not self._is_rune_code(first_extra):
                return "Tablet"
        return "Classic"

    def _is_pierce_row(self, raw: Dict[str, str]) -> bool:
        if self._is_craft_row(raw):
            return False
        mod_codes = self._row_mod_codes(raw)
        if mod_codes & self._pierce_mods or any(code.startswith("pierce-") for code in mod_codes):
            return True
        out_raw = raw.get("output", "").strip()
        if not out_raw:
            return False
        out_base, out_flags, _ = self.parse_token(out_raw)
        for flag in out_flags:
            if flag.lower().startswith("pre="):
                pre_row = self.prefixes.get(flag.split("=", 1)[1].strip())
                if pre_row:
                    for idx in range(1, 4):
                        if pre_row.get(f"mod{idx}code", "").strip().lower().startswith("pierce-"):
                            return True
        unique_row = self.unique_items_by_name.get(out_base.casefold())
        if unique_row:
            for idx in range(1, 13):
                prop = unique_row.get(f"prop{idx}", "").strip()
                if not prop:
                    continue
                prefix_part = prop.split("-", 1)[0].strip().casefold()
                if "-affix" in prop.lower() and prefix_part in self._pierce_prefix_to_mod:
                    return True
        return False

    def _is_tier_upgrade_row(self, raw: Dict[str, str]) -> bool:
        outputs = self._row_outputs(raw)
        inputs = self._row_inputs(raw)
        if not outputs or not inputs:
            return False
        out_base, out_flags, _ = self.parse_token(outputs[0])
        out_q = {self.canonical_qualifier(f) for f in out_flags}
        if out_q & {"exc", "eli"}:
            return True
        in1_base, in1_flags, _ = self.parse_token(inputs[0])
        in1_q = {self.canonical_qualifier(f) for f in in1_flags}
        if out_base.lower() == "usetype" and "nor" in out_q and "low" in in1_q:
            return True
        if in1_base.lower() == "any" and (in1_q & {"set", "uni"}) and out_base.lower() == "usetype" and (out_q & {"set", "uni"}):
            return True
        return False

    def _is_repair_row(self, raw: Dict[str, str]) -> bool:
        mod_codes = self._row_mod_codes(raw)
        if mod_codes & {"rep-dur", "rep-quant"}:
            return True
        for out in self._row_outputs(raw):
            _, flags, _ = self.parse_token(out)
            if {f.lower() for f in flags} & {"rep", "rch"}:
                return True
        return False

    def _is_portal_or_quest_row(self, raw: Dict[str, str]) -> bool:
        if raw.get("op", "").strip() == "28":
            return True
        outputs = self._row_outputs(raw)
        if any("portal" in self.parse_token(out)[0].lower() for out in outputs):
            return True
        inputs = self._row_inputs(raw)
        if inputs and all(self._find_base_item(self.parse_token(tok)[0]) and (self._find_base_item(self.parse_token(tok)[0]) or {}).get("quest", "").strip() not in {"", "0"} for tok in inputs):
            return True
        return False

    def _is_augment_row(self, raw: Dict[str, str]) -> bool:
        return any(code.startswith("augmented") for code in self._row_mod_codes(raw))

    def _is_block_refund_row(self, raw: Dict[str, str]) -> bool:
        inputs = self._row_inputs(raw)
        outputs = self._row_outputs(raw)
        if len(inputs) < 2 or len(outputs) < 2:
            return False
        out_base = self.parse_token(outputs[0])[0].lower()
        if out_base != "useitem":
            return False
        refund_base = self.parse_token(outputs[-1])[0].lower()
        cat_base = self.parse_token(inputs[-1])[0].lower()
        return bool(cat_base) and refund_base == cat_base and not self._row_mod_codes(raw)

    def _recipe_group_name(self, recipe: CubeRecipeDTO) -> str:
        if recipe.get("status") == "removed":
            return "Removed Baseline Recipes"

        raw = recipe.get("raw_row", {})
        if not raw:
            return "General Recipes"

        if self._is_corruption_row(raw):
            return "Corruption Recipes"
        if self._is_socketing_row(raw):
            return "Socketing & Sockets"
        if self._is_tier_upgrade_row(raw):
            return "Item Upgrades"
        if self._is_craft_row(raw):
            return "Ascended Crafting" if self._craft_source_for_row(raw) == "Ascended" else "Classic Crafting"
        if self._is_pierce_row(raw):
            return "Pierce Amulet Crafting"

        inputs = self._row_inputs(raw)
        outputs = self._row_outputs(raw)
        in_bases = [self.parse_token(tok)[0] for tok in inputs]
        out_bases = [self.parse_token(tok)[0] for tok in outputs]
        in1_base = in_bases[0] if in_bases else ""
        out1_base = out_bases[0] if out_bases else ""

        if self._crafting_catalyst_codes and any(c.lower() in self._crafting_catalyst_codes for c in in_bases[1:] + out_bases):
            return "Crafting Tablets"
        if self._is_repair_row(raw):
            return "Repair & Recharge"
        if self._is_portal_or_quest_row(raw):
            return "Portals & Quest Recipes"
        if self._is_augment_row(raw):
            return "Item Reforging & Cosmetics"

        mod_codes = self._row_mod_codes(raw)
        if self._is_rune_code(in1_base) and self._is_rune_code(out1_base):
            return "Rune Transmutation"

        out1_flags = {self.canonical_qualifier(f) for f in self.parse_token(outputs[0])[1]} if outputs else set()
        in1_is_equip = (
            self.has_item_type(in1_base, "weap")
            or self.has_item_type(in1_base, "armo")
        )
        if mod_codes & {"dyed1", "dyewhite1", "dyeblack1"}:
            return "Item Reforging & Cosmetics"
        if out1_base.lower() == "useitem" and mod_codes == {"ethereal"}:
            return "Item Reforging & Cosmetics"
        if out1_base.lower() == "usetype" and in1_is_equip and (out1_flags & {"rar", "mag", "tmp"}):
            return "Item Reforging & Cosmetics"
        if out1_base.lower() == "useitem" and "tmp" in out1_flags and in1_is_equip:
            return "Item Reforging & Cosmetics"
        if self._is_block_refund_row(raw) and (self.has_item_type(in1_base, "weap") or self.has_item_type(in1_base, "armo")):
            return "Item Reforging & Cosmetics"

        is_charm_or_jewel = (
            self.has_item_type(in1_base, "char")
            or self.has_item_type(in1_base, "chms")
            or self.has_item_type(in1_base, "jewl")
            or self.has_item_type(out1_base, "char")
            or self.has_item_type(out1_base, "chms")
            or self.has_item_type(out1_base, "jewl")
        )
        is_named_reward = bool(self._find_named_item(out1_base)) or any(
            self.has_item_type(code, "jwly") for code in in_bases[:1] if code
        ) and not (in1_base.lower() in {"amu", "rin"} and out1_base.lower() in {"amu", "rin"})
        if is_charm_or_jewel or is_named_reward:
            return "Charm, Jewel & Reward Recipes"

        if self._is_gem_code(in1_base) or self._is_gem_code(out1_base):
            return "Material Upgrades & Conversions"
        if self._is_rune_code(in1_base) and not self._is_rune_code(out1_base):
            return "Material Upgrades & Conversions"
        if self.has_item_type(in1_base, "spot") and (self.has_item_type(out1_base, "spot") or self._is_rune_code(out1_base) or self.has_item_type(out1_base, "elix")):
            return "Material Upgrades & Conversions"
        if self.has_item_type(out1_base, "spot") and any(self.has_item_type(c, "spot") for c in in_bases):
            return "Material Upgrades & Conversions"

        utility_types = ("poti", "hpot", "mpot", "rpot", "wpot", "key", "scro", "book", "bowq", "xboq", "ukey")
        if any(self.has_item_type(in1_base, ut) or self.has_item_type(out1_base, ut) for ut in utility_types) or (
            in1_base and in1_base.lower() == out1_base.lower()
        ):
            return "Stacking & Utility"

        return "General Recipes"

    def display_title(self, recipe: CubeRecipeDTO) -> str:
        """Generates a localized player-facing recipe title from resolved inputs, outputs, and modifiers."""
        if recipe.get("id") in self._condensed_recipe_ids:
            return recipe.get("description", "")

        inputs = [str(inp).strip() for inp in recipe.get("inputs", []) if str(inp).strip()]
        outputs = [str(out).strip() for out in recipe.get("outputs", []) if str(out).strip()]
        raw = recipe.get("raw_row", {})
        if not inputs and not outputs:
            return recipe.get("description", "")

        left = " + ".join(inputs)
        right = ", ".join(outputs)
        if raw:
            out_raw = raw.get("output", "").strip()
            out_base, out_flags, _ = self.parse_token(out_raw)
            non_marker_mods = [
                text
                for code, param, mn, mx in self._row_mods(raw)
                if not code.lower().startswith(("corruption", "augmented"))
                and code.lower() != "state"
                for text in [self.resolver.resolve_property(code, param, mn, mx).get("resolved_text", "").strip()]
                if text and not text.startswith("Unknown property (")
            ]
            deduped_mods = list(dict.fromkeys(non_marker_mods))
            if deduped_mods:
                if out_base.lower() == "useitem" and not out_flags and not raw.get("output b", "").strip():
                    right = "; ".join(deduped_mods)
                elif not self._is_craft_row(raw) and not raw.get("output b", "").strip():
                    right = f"{self.resolve_token(out_raw)} ({'; '.join(deduped_mods)})"

        if left and right:
            return f"{left} \u2192 {right}"
        return left or right or recipe.get("description", "")

    def _corruption_summaries(self, recipes: List[CubeRecipeDTO]) -> List[Dict[str, Any]]:
        grouped: Dict[Tuple[str, ...], List[CubeRecipeDTO]] = {}
        display_inputs: Dict[Tuple[str, ...], List[str]] = {}
        for recipe in recipes:
            value = self._to_int(recipe.get("raw_row", {}).get("value"))
            if not recipe.get("inputs") or value <= 0:
                continue
            key = self._corruption_raw_input_key(recipe)
            if not key:
                continue
            grouped.setdefault(key, []).append(recipe)
            display_inputs.setdefault(key, recipe["inputs"])

        summaries: List[Dict[str, Any]] = []
        for key, rows in grouped.items():
            if self._is_parent_only_corruption_group(key, rows, grouped):
                continue
            expanded_rows = self._corruption_parent_rows(key, grouped) + rows
            outcomes = self._corruption_outcomes(expanded_rows)
            if not outcomes:
                continue
            inputs = list(display_inputs[key])
            first_base, first_flags, _ = self.parse_token(key[0])
            target_qualities = [
                canonical
                for flag in first_flags
                for canonical in [self.canonical_qualifier(flag)]
                if canonical in self.CORRUPTION_RARITY_ORDER
            ]
            target_label = self.get_item_name(first_base)
            target_chain = self.item_type_chain_for_token(first_base)
            is_named_unique = bool(self._find_named_item(first_base)) or (
                bool(first_base)
                and first_base.lower() not in {"any"}
                and first_base not in self.item_types
                and first_base.lower() not in self._item_types_by_code_ci
                and not self._find_base_item(first_base)
            )
            material_code = self.parse_token(key[-1])[0].lower() if len(key) > 1 else ""
            material_name = inputs[-1] if len(inputs) > 1 else ""

            summaries.append(
                {
                    "id": slugify(" ".join(key)),
                    "inputs": inputs,
                    "title": " + ".join(inputs),
                    "target_code": first_base.lower(),
                    "target_label": target_label,
                    "target_qualities": target_qualities,
                    "target_type_chain": target_chain,
                    "is_named_unique": is_named_unique,
                    "material_code": material_code,
                    "material": material_name,
                    "outcomes": outcomes,
                    "search_text": " ".join(
                        inputs + [outcome["label"] for outcome in outcomes] + [outcome["detail"] for outcome in outcomes if outcome.get("detail")]
                    ),
                }
            )
        return sorted(summaries, key=lambda summary: (summary["material"], summary["title"]))

    @staticmethod
    def _corruption_raw_input_key(recipe: CubeRecipeDTO) -> Tuple[str, ...]:
        raw = recipe.get("raw_row", {})
        values = []
        for index in range(1, 8):
            value = raw.get(f"input {index}", "").strip().strip('"')
            if value and value != "0":
                values.append(value)
        return tuple(values)

    def _corruption_parent_rows(
        self,
        key: Tuple[str, ...],
        grouped: Dict[Tuple[str, ...], List[CubeRecipeDTO]],
    ) -> List[CubeRecipeDTO]:
        if len(key) < 2:
            return []

        first_token = key[0]
        token_parts = first_token.split(",")
        item_type = token_parts[0]
        qualifiers = token_parts[1:]
        parent_rows: List[CubeRecipeDTO] = []
        for parent_type in self._item_type_ancestors(item_type):
            parent_token = ",".join([parent_type] + qualifiers)
            parent_key = (parent_token,) + key[1:]
            parent_rows.extend(
                recipe
                for recipe in grouped.get(parent_key, [])
                if self._is_parent_corruption_outcome(recipe)
            )
        return parent_rows

    def _item_type_ancestors(self, item_type: str) -> List[str]:
        ancestors: List[str] = self._inferred_type_parents.get(item_type, []).copy()
        seen = set(ancestors)

        def walk(code: str) -> None:
            for extra in self._inferred_type_parents.get(code, []):
                if extra not in seen:
                    seen.add(extra)
                    ancestors.append(extra)
                    walk(extra)
            row = self.item_types.get(code)
            if not row:
                return
            for column in ("Equiv1", "Equiv2"):
                parent = row.get(column, "").strip()
                if not parent or parent in seen:
                    continue
                seen.add(parent)
                ancestors.append(parent)
                walk(parent)

        walk(item_type)
        if item_type != "any" and "any" not in seen:
            ancestors.append("any")
        return ancestors

    def _is_parent_corruption_outcome(self, recipe: CubeRecipeDTO) -> bool:
        return self._is_brick_corruption_row(recipe.get("raw_row", {}))

    def _is_parent_only_corruption_group(
        self,
        key: Tuple[str, ...],
        rows: List[CubeRecipeDTO],
        grouped: Dict[Tuple[str, ...], List[CubeRecipeDTO]],
    ) -> bool:
        has_specific_outcome = any(
            self._to_int(recipe.get("raw_row", {}).get("value")) > 0
            and not self._is_brick_corruption_row(recipe.get("raw_row", {}))
            for recipe in rows
        )
        if has_specific_outcome:
            return False

        if len(key) < 2:
            return False

        first_code = key[0].split(",", 1)[0]
        for candidate_key, candidate_rows in grouped.items():
            if candidate_key == key or len(candidate_key) < 2 or candidate_key[1:] != key[1:]:
                continue
            candidate_code = candidate_key[0].split(",", 1)[0]
            if first_code not in self._item_type_ancestors(candidate_code):
                continue
            if any(
                not self._is_brick_corruption_row(recipe.get("raw_row", {}))
                and self._to_int(recipe.get("raw_row", {}).get("value")) > 0
                for recipe in candidate_rows
            ):
                return True
        return False

    def _corruption_outcomes(self, rows: List[CubeRecipeDTO]) -> List[Dict[str, Any]]:
        sorted_rows = sorted(
            rows,
            key=lambda recipe: (self._to_int(recipe["raw_row"].get("value")), recipe.get("description", "")),
        )
        previous = 0
        outcomes: List[Dict[str, Any]] = []
        for recipe in sorted_rows:
            threshold = min(1000, self._to_int(recipe["raw_row"].get("value")))
            span = threshold - previous
            if span <= 0:
                continue
            outcomes.append(
                {
                    "label": self._corruption_outcome_label(recipe),
                    "detail": self._corruption_outcome_detail(recipe),
                    "chance": self._format_corruption_percent(span),
                    "range": f"{previous + 1}-{threshold}",
                    "status": recipe.get("status", "unchanged"),
                }
            )
            previous = threshold

        if outcomes and previous < 1000:
            outcomes.append(
                {
                    "label": "Successful corruption roll",
                    "detail": "Falls through to the general corruption result for this item type.",
                    "chance": self._format_corruption_percent(1000 - previous),
                    "range": f"{previous + 1}-1000",
                    "status": "unchanged",
                }
            )
        return outcomes

    def _non_marker_corruption_mods(self, raw: Dict[str, str]) -> List[Tuple[str, str, str, str]]:
        return [
            (code, param, mn, mx)
            for code, param, mn, mx in self._row_mods(raw)
            if not code.lower().startswith("corruption")
        ]

    def _corruption_outcome_label(self, recipe: CubeRecipeDTO) -> str:
        raw = recipe.get("raw_row", {})
        if self._is_brick_corruption_row(raw):
            for out in self._row_outputs(raw):
                base_code = self.parse_token(out)[0]
                if base_code.lower() == "brk":
                    return self.get_item_name(base_code)
            return self.get_item_name("brk")

        non_markers = self._non_marker_corruption_mods(raw)
        sock_mod = next((m for m in non_markers if m[0].lower() == "sock"), None)
        if sock_mod:
            _, _, s_min, s_max = sock_mod
            if s_min and s_min == s_max:
                return self.state_label("sock", s_min)
            if s_min and s_max:
                return self.state_label("sock", f"{s_min}-{s_max}")
            return self.state_label("sock")

        resolved_texts: List[str] = []
        for code, param, mn, mx in non_markers:
            resolved = self.resolver.resolve_property(code, param, mn, mx).get("resolved_text", "").strip()
            if resolved and not resolved.startswith("Unknown property (") and resolved not in resolved_texts:
                resolved_texts.append(resolved)
        if resolved_texts:
            return "; ".join(resolved_texts)

        return ", ".join(recipe.get("outputs", [])) or recipe.get("description", "")

    def _corruption_outcome_detail(self, recipe: CubeRecipeDTO) -> str:
        raw = recipe.get("raw_row", {})
        if self._is_brick_corruption_row(raw):
            main_out = self.resolve_token(raw.get("output", ""))
            extra_outs = [
                self.resolve_token(raw.get(col, ""))
                for col in ("output 2", "output 3", "output b", "output c")
                if raw.get(col, "").strip() not in {"", "0"}
            ]
            extra_outs = [val for val in extra_outs if val]
            if main_out and extra_outs:
                return f"{main_out} (+ {', '.join(extra_outs)})"
            return ", ".join([val for val in [main_out] + extra_outs if val])

        non_markers = self._non_marker_corruption_mods(raw)
        has_sock = any(code.lower() == "sock" for code, _, _, _ in non_markers)
        if has_sock:
            extra_texts = [
                resolved
                for code, param, mn, mx in non_markers
                if code.lower() != "sock"
                for resolved in [self.resolver.resolve_property(code, param, mn, mx).get("resolved_text", "").strip()]
                if resolved and not resolved.startswith("Unknown property (")
            ]
            return "; ".join(extra_texts)
        return ""

    @staticmethod
    def _format_corruption_percent(span: int) -> str:
        value = span / 10
        if value.is_integer():
            return f"{int(value)}%"
        return f"{value:.1f}".rstrip("0").rstrip(".") + "%"

    @staticmethod
    def _to_int(value: Any) -> int:
        try:
            return int(str(value).strip()) if str(value).strip() else 0
        except (TypeError, ValueError):
            return 0

    @staticmethod
    def _is_enabled_recipe_row(row: Dict[str, str]) -> bool:
        if row.get("enabled", "").strip() == "0":
            return False
        return CubeAnalyzerService._has_cube_payload(row)

    @staticmethod
    def _has_cube_payload(row: Dict[str, str]) -> bool:
        input_columns = [f"input {index}" for index in range(1, 8)]
        output_columns = ["output", "output 2", "output 3", "output b", "output c"]
        has_input = any(
            row.get(column, "").strip() not in {"", "0"} for column in input_columns
        )
        has_output = any(
            row.get(column, "").strip() not in {"", "0"} for column in output_columns
        )
        return has_input and has_output

    @staticmethod
    def _recipe_status_counts(recipes: List[CubeRecipeDTO]) -> Dict[str, int]:
        counts = {"added": 0, "modified": 0, "removed": 0, "unchanged": 0}
        for recipe in recipes:
            status = recipe.get("status", "unchanged")
            counts[status] = counts.get(status, 0) + 1
        return counts

    @staticmethod
    def _recipe_sort_key(recipe: CubeRecipeDTO) -> Tuple[int, str]:
        status_order = {"added": 0, "modified": 1, "unchanged": 2, "removed": 3}
        return (status_order.get(recipe.get("status", "unchanged"), 2), recipe.get("description", "").lower())

    def analyze_raw_recipes(self, include_removed: bool = False) -> List[CubeRecipeDTO]:
        recipes_data = self.repo.get_excel_table("cubemain")
        recipes = [
            self.analyze_recipe(row)
            for row in recipes_data
            if self._is_enabled_recipe_row(row)
        ]

        if include_removed and self.retail_repo:
            bk_recipe_keys = {
                row.get("description", "").strip().lower()
                for row in recipes_data
                if row.get("description") and self._is_enabled_recipe_row(row)
            }
            retail_analyzer = CubeAnalyzerService(self.retail_repo)
            for key, row in self.retail_recipe_rows.items():
                if key not in bk_recipe_keys and self._is_enabled_recipe_row(row):
                    recipes.append(retail_analyzer.analyze_recipe(row, status="removed"))
        return recipes


class RecipePresentationBuilder:
    SYSTEM_PAGES = [
        {
            "id": "crafting",
            "title": "Crafting",
            "href": "crafting/",
            "summary": "Blood, Caster, Safety, and Hit Power crafts as item-type matrices.",
            "action": "Compare craft families",
        },
        {
            "id": "corruptions",
            "title": "Corruptions",
            "href": "corruptions/",
            "summary": "Standard and Divine Standard corruption outcomes with chance breakdowns.",
            "action": "Review risk and sockets",
        },
        {
            "id": "pierce",
            "title": "Pierce Crafts",
            "href": "pierce/",
            "summary": "Elemental, magic, poison, and physical pierce recipes grouped by family.",
            "action": "Find pierce recipes",
        },
        {
            "id": "reforge-upgrade",
            "title": "Reforge, Socket, and Upgrade",
            "href": "reforge-upgrade/",
            "summary": "Tier upgrades, Larzuk sockets, Charsi reforges, ethereal changes, and augments.",
            "action": "Shape gear",
        },
        {
            "id": "materials",
            "title": "Runes and Materials",
            "href": "materials/",
            "summary": "Rune ladders, gem conversions, Standards, Bricks, Sigils, keys, and utility recipes.",
            "action": "Convert materials",
        },
        {
            "id": "all",
            "title": "All Recipes",
            "href": "all/",
            "summary": "Every player-facing cube recipe in one searchable table.",
            "action": "Search everything",
        },
        {
            "id": "raw",
            "title": "Technical Raw Rows",
            "href": "raw/",
            "summary": "Exact enabled cubemain rows for technical drilldown.",
            "action": "Inspect source rows",
        },
    ]

    _TARGET_FAMILY_ORDER: Dict[str, int] = {
        "tors": 10,
        "helm": 20,
        "boot": 30,
        "glov": 40,
        "2han": 50,
        "bow": 60,
        "xbow": 70,
        "amul": 80,
        "amu": 80,
        "ring": 90,
        "rin": 90,
    }

    def __init__(self, analyzer: CubeAnalyzerService, raw_recipes: List[CubeRecipeDTO], groups: List[CubeRecipeGroupDTO]):
        self.analyzer = analyzer
        self.raw_recipes = raw_recipes
        self.groups = groups
        self.group_by_id = {group["id"]: group for group in groups}

    def build(self) -> Dict[str, Any]:
        crafting = self.crafting_page()
        corruptions = self.corruptions_page()
        pierce = self.pierce_page()
        reforge = self.reforge_upgrade_page()
        materials = self.materials_page()
        all_recipes = self.all_page(crafting, corruptions, pierce, reforge, materials)
        raw = self.raw_page()
        overview = self.overview_page(crafting, corruptions, pierce, reforge, materials, all_recipes, raw)
        return {
            "overview": overview,
            "crafting": crafting,
            "corruptions": corruptions,
            "pierce": pierce,
            "reforge_upgrade": reforge,
            "materials": materials,
            "all": all_recipes,
            "raw": raw,
        }

    def overview_page(self, crafting, corruptions, pierce, reforge, materials, all_recipes, raw) -> Dict[str, Any]:
        sections = corruptions.get("sections", [])
        corruption_cards = (
            sum(len(section["summaries"]) for section in sections)
            if sections
            else (
                len(corruptions["combined_summaries"])
                + len(corruptions["standard_summaries"])
                + len(corruptions["divine_summaries"])
            )
        )
        counts = {
            "raw_enabled_rows": len([recipe for recipe in self.raw_recipes if recipe.get("status") != "removed"]),
            "display_groups": len(self.groups),
            "craft_rows": sum(len(section["rows"]) for section in crafting["sections"]),
            "corruption_cards": corruption_cards,
            "raw_rows": len(raw["rows"]),
        }
        cards = []
        page_counts = {
            "crafting": counts["craft_rows"],
            "corruptions": counts["corruption_cards"],
            "pierce": len(pierce["families"]),
            "reforge-upgrade": len(reforge["sections"]),
            "materials": sum(len(section["rows"]) for section in materials["sections"]),
            "all": len(all_recipes["rows"]),
            "raw": counts["raw_rows"],
        }
        for card in self.SYSTEM_PAGES:
            entry = dict(card)
            entry["count"] = page_counts.get(card["id"], 0)
            cards.append(entry)
        return {"counts": counts, "cards": cards}

    def crafting_page(self) -> Dict[str, Any]:
        craft_recipes = [
            recipe
            for recipe in self.raw_recipes
            if self.analyzer._is_craft_row(recipe.get("raw_row", {}))
            and "mag" in self._token_parts(recipe.get("raw_row", {}).get("input 1", ""))
        ]
        grouped: Dict[Tuple[str, str, str], List[CubeRecipeDTO]] = {}
        for recipe in craft_recipes:
            raw = recipe["raw_row"]
            source = self._craft_source(raw)
            family = self._craft_family(raw, recipe["description"])
            item_type = self._base_name(self._token_base(raw.get("input 1", "")))
            grouped.setdefault((source, family, item_type), []).append(recipe)

        sections_by_key: Dict[Tuple[str, str], Dict[str, Any]] = {}
        for (source, family, item_type), recipes in grouped.items():
            key = (source, family)
            section = sections_by_key.setdefault(
                key,
                {
                    "id": slugify(f"{source} {family}"),
                    "source": source,
                    "family": family,
                    "filter_tags": slugify(family),
                    "title": f"{source} {family}",
                    "summary": self._craft_summary(source, family),
                    "rows": [],
                },
            )
            variants = []
            seen_variants = set()
            for recipe in sorted(recipes, key=lambda candidate: self._craft_variant_name(candidate["raw_row"])):
                raw = recipe["raw_row"]
                variant_label = self._craft_variant_name(raw)
                variant_key = (
                    variant_label,
                    tuple(raw.get(f"input {index}", "").strip() for index in range(2, 8)),
                    tuple(raw.get(f"mod {index}", "").strip() for index in range(1, 6)),
                    tuple(raw.get(f"mod {index} min", "").strip() for index in range(1, 6)),
                    tuple(raw.get(f"mod {index} max", "").strip() for index in range(1, 6)),
                )
                if variant_key in seen_variants:
                    continue
                seen_variants.add(variant_key)
                variants.append(
                    {
                        "variant": variant_label,
                        "ingredients": self._ingredient_labels(raw, start=2),
                        "output": self.analyzer.resolve_output(raw.get("output", "")),
                        "fixed_properties": self._fixed_properties(raw),
                    }
                )
            section["rows"].append(
                {
                    "item_type": item_type,
                    "variants": variants,
                    "search_text": " ".join(
                        [source, family, item_type]
                        + [
                            " ".join([variant["variant"], " ".join(variant["ingredients"]), " ".join(variant["fixed_properties"])])
                            for variant in variants
                        ]
                    ),
                }
            )

        sections = list(sections_by_key.values())
        for section in sections:
            section["rows"] = sorted(section["rows"], key=lambda row: row["item_type"])
        filters = [
            {
                "value": slugify(family),
                "label": family,
                "count": sum(len(section["rows"]) for section in sections if section["family"] == family),
            }
            for family in sorted({section["family"] for section in sections})
        ]
        return {
            "sections": sorted(sections, key=lambda section: (section["source"], section["family"])),
            "filters": filters,
        }

    def corruptions_page(self) -> Dict[str, Any]:
        corruption_group = self.group_by_id.get("corruption", {"recipes": [], "corruption_summaries": []})
        summaries = [dict(summary) for summary in corruption_group.get("corruption_summaries", [])]

        by_material: Dict[str, List[Dict[str, Any]]] = {}
        material_titles: Dict[str, str] = {}
        for summary in summaries:
            summary["filter_tags"] = "|".join(self._corruption_filter_tags(summary))
            mat_code = str(summary.get("material_code") or "").strip().lower()
            if not mat_code:
                mat_code = slugify(summary.get("material", "")) or "other"
            by_material.setdefault(mat_code, []).append(summary)
            if summary.get("material"):
                material_titles.setdefault(mat_code, summary["material"])

        for mat_code in list(by_material.keys()):
            by_material[mat_code] = self._group_corruption_equivalent_summaries(
                by_material[mat_code], analyzer=self.analyzer
            )

        std_name = material_titles.get("std") or self.analyzer.get_item_name("std")
        dsd_name = material_titles.get("dsd") or self.analyzer.get_item_name("dsd")
        std_rows = by_material.pop("std", [])
        dsd_rows = by_material.pop("dsd", [])

        combined_material_label = (
            f"{std_name} or {dsd_name}"
            if getattr(self.analyzer.repo, "locale", "enUS") == "enUS"
            else f"{std_name} / {dsd_name}"
        )
        if std_rows and dsd_rows:
            combined, remaining_standard, remaining_divine = self._group_corruption_material_equivalent_summaries(
                std_rows, dsd_rows, combined_material_label=combined_material_label
            )
        else:
            combined, remaining_standard, remaining_divine = [], std_rows, dsd_rows

        combined = self._group_corruption_target_equivalent_summaries(combined)
        remaining_standard = self._group_corruption_target_equivalent_summaries(remaining_standard)
        remaining_divine = self._group_corruption_target_equivalent_summaries(remaining_divine)

        sections: List[Dict[str, Any]] = []
        if combined:
            sections.append({"id": "either-standard-corruptions", "title": combined_material_label, "summaries": combined})
        if remaining_standard:
            sections.append({"id": "standard-corruptions", "title": std_name, "summaries": remaining_standard})
        if remaining_divine:
            sections.append({"id": "divine-corruptions", "title": dsd_name, "summaries": remaining_divine})

        for mat_code in sorted(by_material.keys()):
            mat_summaries = self._group_corruption_target_equivalent_summaries(by_material[mat_code])
            if not mat_summaries:
                continue
            mat_title = material_titles.get(mat_code) or mat_summaries[0].get("material") or mat_code
            sections.append(
                {
                    "id": f"material-{slugify(mat_code)}",
                    "title": mat_title,
                    "summaries": mat_summaries,
                }
            )

        repo = self.analyzer.repo
        charms_lbl = resolve_localized_string(repo, "Charm") or "Charms"
        weapons_lbl = resolve_localized_string(repo, "StrGemX3").rstrip(": ").strip() or "Weapons"
        shields_lbl = resolve_localized_string(repo, "shlds") or "Shields"
        armor_lbl = resolve_localized_string(repo, "armor")
        wearables_lbl = "Armor & Wearables" if (not armor_lbl or armor_lbl.lower() == "armor") else armor_lbl
        unique_lbl = resolve_localized_string(repo, "LootFilterUniqueRarity")
        named_uniques_lbl = "Named Uniques" if (not unique_lbl or unique_lbl.lower() == "unique") else unique_lbl

        filter_defs = [
            ("charms", charms_lbl),
            ("weapons", weapons_lbl),
            ("wearables", wearables_lbl),
            ("shields", shields_lbl),
            ("jewelry", "Jewelry"),
            ("any-item", self.analyzer.get_item_name("any")),
            ("named-uniques", named_uniques_lbl),
        ]
        all_summaries = [summary for section in sections for summary in section["summaries"]]
        return {
            "sections": sections,
            "combined_summaries": combined,
            "standard_summaries": remaining_standard,
            "divine_summaries": remaining_divine,
            "raw_count": len(corruption_group.get("recipes", [])),
            "filters": [
                {
                    "value": value,
                    "label": label,
                    "count": len([summary for summary in all_summaries if value in summary.get("filter_tags", "").split("|")]),
                }
                for value, label in filter_defs
                if any(value in summary.get("filter_tags", "").split("|") for summary in all_summaries)
            ],
        }

    @staticmethod
    def _group_corruption_target_equivalent_summaries(summaries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        grouped: Dict[Tuple[Any, ...], List[Dict[str, Any]]] = {}
        passthrough: List[Dict[str, Any]] = []

        for summary in summaries:
            inputs = summary.get("inputs", [])
            if len(inputs) < 2:
                passthrough.append(summary)
                continue
            family = RecipePresentationBuilder._corruption_target_family(summary)
            if not family:
                passthrough.append(summary)
                continue
            outcomes = tuple(
                (
                    outcome.get("label", ""),
                    outcome.get("detail", ""),
                    outcome.get("chance", ""),
                    outcome.get("range", ""),
                )
                for outcome in summary.get("outcomes", [])
            )
            key = (family, inputs[-1], outcomes)
            grouped.setdefault(key, []).append(summary)

        result = passthrough[:]
        for (_family, material, _outcomes), rows in grouped.items():
            if len(rows) == 1:
                result.append(rows[0])
                continue

            first = dict(rows[0])
            target = RecipePresentationBuilder._combined_corruption_target_label_from_rows(rows)
            filter_tags = RecipePresentationBuilder._combined_filter_tags(rows)
            first["inputs"] = [target, material]
            first["title"] = " + ".join(first["inputs"])
            first["id"] = slugify(" ".join(first["inputs"]))
            first["filter_tags"] = filter_tags
            first["search_text"] = " ".join(
                [first["title"]]
                + [row.get("title", "") for row in rows]
                + [row.get("search_text", "") for row in rows]
            )
            result.append(first)

        return sorted(result, key=lambda summary: (summary["material"], summary["title"]))

    @staticmethod
    def _corruption_target_family(summary_or_target: Any) -> str:
        if isinstance(summary_or_target, dict) and "target_type_chain" in summary_or_target:
            if summary_or_target.get("is_named_unique"):
                return ""
            chain = set(summary_or_target.get("target_type_chain") or [])
            code = str(summary_or_target.get("target_code") or "").strip().lower()
            if chain & {"char", "scha", "mcha", "lcha"}:
                return ""
            if chain & {"tors", "helm", "boot", "glov"} or code in {"tors", "helm", "boot", "glov"}:
                return "wearable-armor"
            if code in {"2han", "bow", "xbow"} or (chain & {"bow", "xbow"}):
                return "weapon-subtypes"
            if code in {"amul", "amu", "ring", "rin"} or (chain & {"amul", "ring"}):
                return "jewelry"
            return ""

        target = summary_or_target.get("inputs", [""])[0] if isinstance(summary_or_target, dict) else str(summary_or_target)
        label, _rarities = RecipePresentationBuilder._corruption_target_label_and_rarities(target)
        normalized = label.lower()
        if normalized in {"armor", "helm", "helmet", "boots", "gloves"}:
            return "wearable-armor"
        if normalized in {"2handed melee weapon", "bow", "crossbow"}:
            return "weapon-subtypes"
        if normalized in {"amulet", "ring"}:
            return "jewelry"
        return ""

    @staticmethod
    def _combined_corruption_target_label_from_rows(rows: List[Dict[str, Any]]) -> str:
        order_legacy = {
            "armor": 10,
            "helm": 20,
            "helmet": 21,
            "boots": 30,
            "gloves": 40,
            "2handed melee weapon": 50,
            "bow": 60,
            "crossbow": 70,
            "amulet": 80,
            "ring": 90,
        }
        unique_parsed: List[Tuple[int, str, str]] = []
        seen: Set[Tuple[str, str]] = set()
        for row in rows:
            target = row["inputs"][0]
            label, rarities = RecipePresentationBuilder._corruption_target_label_and_rarities(target)
            key = (label, rarities)
            if key in seen:
                continue
            seen.add(key)
            code = str(row.get("target_code") or "").strip().lower()
            rank = RecipePresentationBuilder._TARGET_FAMILY_ORDER.get(
                code, order_legacy.get(label.lower(), 999)
            )
            unique_parsed.append((rank, label, rarities))

        unique_parsed = sorted(unique_parsed, key=lambda item: (item[0], item[1], item[2]))
        rarity_sets = {rarities for _, _, rarities in unique_parsed}
        if len(rarity_sets) == 1:
            rarities = next(iter(rarity_sets))
            labels = ", ".join(label for _, label, _ in unique_parsed)
            return f"{labels} ({rarities})" if rarities else labels

        return " or ".join(
            f"{label} ({rarities})" if rarities else label
            for _, label, rarities in unique_parsed
        )

    @staticmethod
    def _combined_corruption_target_label(targets: List[str]) -> str:
        return RecipePresentationBuilder._combined_corruption_target_label_from_rows(
            [{"inputs": [target]} for target in targets]
        )

    @staticmethod
    def _corruption_target_label_and_rarities(target: str) -> Tuple[str, str]:
        match = _CORRUPTION_TARGET_LEGACY_RE.match(target.strip())
        if not match:
            return target, ""
        return match.group("label"), match.group("rarities")

    @staticmethod
    def _combined_filter_tags(rows: List[Dict[str, Any]]) -> str:
        tags: List[str] = []
        for row in rows:
            for tag in row.get("filter_tags", "").split("|"):
                if tag and tag not in tags:
                    tags.append(tag)
        return "|".join(tags)

    @staticmethod
    def _group_corruption_material_equivalent_summaries(
        standard: List[Dict[str, Any]],
        divine: List[Dict[str, Any]],
        combined_material_label: str = "Standard of Heroes or The Divine Standard",
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
        def normalize_detail(detail: str) -> str:
            return str(detail or "").split(" (+ ", 1)[0].strip()

        def merge_detail(std_detail: str, dsd_detail: str) -> str:
            if std_detail == dsd_detail:
                return std_detail
            base_s = normalize_detail(std_detail)
            base_d = normalize_detail(dsd_detail)
            if base_s == base_d and " (+ " in std_detail and " (+ " in dsd_detail:
                ext_s = std_detail.split(" (+ ", 1)[1].rstrip(")")
                ext_d = dsd_detail.split(" (+ ", 1)[1].rstrip(")")
                if ext_s and ext_d and ext_s != ext_d:
                    return f"{base_s} (+ {ext_s} / {ext_d})"
            return f"{std_detail} / {dsd_detail}" if dsd_detail else std_detail

        def signature(summary: Dict[str, Any]) -> Tuple[Any, ...]:
            inputs = summary.get("inputs", [])
            target = inputs[0] if inputs else summary.get("title", "")
            outcomes = tuple(
                (
                    outcome.get("label", ""),
                    normalize_detail(outcome.get("detail", "")),
                    outcome.get("chance", ""),
                    outcome.get("range", ""),
                )
                for outcome in summary.get("outcomes", [])
            )
            return (target, summary.get("filter_tags", ""), outcomes)

        divine_by_signature = {signature(summary): summary for summary in divine}
        matched_divine_signatures = set()
        combined: List[Dict[str, Any]] = []
        remaining_standard: List[Dict[str, Any]] = []

        for standard_summary in standard:
            sig = signature(standard_summary)
            divine_summary = divine_by_signature.get(sig)
            if not divine_summary:
                remaining_standard.append(standard_summary)
                continue

            matched_divine_signatures.add(sig)
            first = dict(standard_summary)
            merged_outcomes = []
            for s_out, d_out in zip(standard_summary.get("outcomes", []), divine_summary.get("outcomes", [])):
                updated = dict(s_out)
                updated["detail"] = merge_detail(s_out.get("detail", ""), d_out.get("detail", ""))
                merged_outcomes.append(updated)
            first["outcomes"] = merged_outcomes or list(standard_summary.get("outcomes", []))
            first["inputs"] = [standard_summary["inputs"][0], combined_material_label]
            first["title"] = " + ".join(first["inputs"])
            first["id"] = slugify(" ".join(first["inputs"]))
            first["material"] = combined_material_label
            first["material_code"] = "std+dsd"
            first["search_text"] = " ".join(
                [
                    first["title"],
                    standard_summary.get("title", ""),
                    divine_summary.get("title", ""),
                    standard_summary.get("search_text", ""),
                    divine_summary.get("search_text", ""),
                ]
            )
            combined.append(first)

        remaining_divine = [
            summary for summary in divine
            if signature(summary) not in matched_divine_signatures
        ]

        return (
            sorted(combined, key=lambda summary: summary["title"]),
            sorted(remaining_standard, key=lambda summary: (summary["material"], summary["title"])),
            sorted(remaining_divine, key=lambda summary: (summary["material"], summary["title"])),
        )

    @staticmethod
    def _group_corruption_equivalent_summaries(
        summaries: List[Dict[str, Any]],
        analyzer: Optional[CubeAnalyzerService] = None,
    ) -> List[Dict[str, Any]]:
        grouped: Dict[Tuple[Any, ...], List[Dict[str, Any]]] = {}
        passthrough: List[Dict[str, Any]] = []

        for summary in summaries:
            inputs = summary.get("inputs", [])
            if len(inputs) < 2:
                passthrough.append(summary)
                continue

            if "target_qualities" in summary and "target_label" in summary:
                qualities = summary.get("target_qualities") or []
                if not qualities:
                    passthrough.append(summary)
                    continue
                target_label = summary["target_label"]
            else:
                target_label, rarity = RecipePresentationBuilder._corruption_target_parts(inputs[0])
                if not rarity:
                    passthrough.append(summary)
                    continue

            signature = tuple(
                (
                    outcome.get("label", ""),
                    outcome.get("detail", ""),
                    outcome.get("chance", ""),
                    outcome.get("range", ""),
                )
                for outcome in summary.get("outcomes", [])
            )
            key = (inputs[-1], target_label, summary.get("filter_tags", ""), signature)
            grouped.setdefault(key, []).append(summary)

        result = passthrough[:]
        rarity_order_legacy = {"Crafted": 0, "Magic": 1, "Rare": 2, "Set": 3, "Unique": 4}
        code_order = {code: idx for idx, code in enumerate(CubeAnalyzerService.CORRUPTION_RARITY_ORDER)}

        for (_material, target_label, _filter_tags, _signature), rows in grouped.items():
            if len(rows) == 1:
                result.append(rows[0])
                continue

            if "target_qualities" in rows[0] and analyzer is not None:
                seen_codes: List[str] = []
                for row in rows:
                    for code in row.get("target_qualities") or []:
                        if code not in seen_codes:
                            seen_codes.append(code)
                seen_codes = sorted(seen_codes, key=lambda code: (code_order.get(code, 99), code))
                rarity_labels = [analyzer.qualifier_label(code) for code in seen_codes]
                first = dict(rows[0])
                first["target_qualities"] = seen_codes
            else:
                rarity_labels = []
                for row in rows:
                    _, rarity = RecipePresentationBuilder._corruption_target_parts(row["inputs"][0])
                    if rarity and rarity not in rarity_labels:
                        rarity_labels.append(rarity)
                rarity_labels = sorted(
                    rarity_labels, key=lambda r: (rarity_order_legacy.get(r, 99), r)
                )
                first = dict(rows[0])

            first["inputs"] = [f"{target_label} ({', '.join(rarity_labels)})", rows[0]["inputs"][-1]]
            first["title"] = " + ".join(first["inputs"])
            first["id"] = slugify(" ".join(first["inputs"]))
            first["search_text"] = " ".join(
                [first["title"]]
                + [row.get("title", "") for row in rows]
                + [row.get("search_text", "") for row in rows]
            )
            result.append(first)

        return sorted(result, key=lambda summary: (summary["material"], summary["title"]))

    @staticmethod
    def _corruption_target_parts(target: str) -> Tuple[str, str]:
        match = _CORRUPTION_RARITY_LEGACY_RE.match(target.strip())
        if not match:
            return target, ""
        return match.group("label"), match.group("rarity")

    @staticmethod
    def _corruption_filter_tags(summary: Dict[str, Any]) -> List[str]:
        tags: List[str] = []

        def add(tag: str) -> None:
            if tag and tag not in tags:
                tags.append(tag)

        if "target_type_chain" in summary:
            chain = set(summary.get("target_type_chain") or [])
            target_code = str(summary.get("target_code") or "").strip().lower()
            is_named_unique = bool(summary.get("is_named_unique"))
            is_charm = bool(chain & {"char", "scha", "mcha", "lcha"})

            if is_charm:
                if is_named_unique and target_code:
                    add(slugify(target_code))
                add("charms")
                return tags
            if target_code == "any":
                add("any-item")
                return tags
            if is_named_unique:
                add("named-uniques")
                return tags
            if chain & {"weap", "mele", "miss", "bow", "xbow", "2han"}:
                add("weapons")
            if chain & {"shld", "shie", "head", "ashd"}:
                add("shields")
            if chain & {"tors", "helm", "circ", "pelt", "phlm"}:
                add("armor")
                add("wearables")
            elif "armo" in chain and not (chain & {"shld", "shie", "belt", "boot", "glov"}):
                add("armor")
                add("wearables")
            if "belt" in chain:
                add("belts")
                add("wearables")
            if "boot" in chain:
                add("boots")
                add("wearables")
            if "glov" in chain:
                add("gloves")
                add("wearables")
            if chain & {"amul", "ring", "jwly"}:
                add("jewelry")
            return tags or ["other"]

        # Legacy fallback for direct staticmethod calls with mock summary dicts lacking target_type_chain.
        inputs = summary.get("inputs", [])
        target = inputs[0] if inputs else summary.get("title", "")
        normalized = target.lower()

        specific_tags = {
            "annihilus": "annihilus",
            "hellfire torch": "hellfire-torch",
            "gheed's fortune": "gheeds-fortune",
        }
        for marker, tag in specific_tags.items():
            if marker in normalized:
                add(tag)

        if any(marker in normalized for marker in ("annihilus", "hellfire torch", "gheed's fortune")):
            add("charms")
        if "any item" in normalized:
            add("any-item")
        if any(marker in normalized for marker in ("weapon", "2handed", "bow", "crossbow")):
            add("weapons")
        if any(marker in normalized for marker in ("armor", "helm", "helmet")):
            add("armor")
            add("wearables")
        if "shield" in normalized:
            add("shields")
        if "amulet" in normalized or "ring" in normalized:
            add("jewelry")
        if "belt" in normalized:
            add("belts")
            add("wearables")
        if "boots" in normalized:
            add("boots")
            add("wearables")
        if "gloves" in normalized:
            add("gloves")
            add("wearables")

        generic_markers = (
            "annihilus", "hellfire torch", "gheed's fortune", "2handed",
            "amulet", "any item", "any shield", "armor", "belt", "boots",
            "bow", "crossbow", "gloves", "helm", "helmet", "ring", "weapon",
        )
        if not any(marker in normalized for marker in generic_markers):
            add("named-uniques")

        return tags or ["other"]

    def _pierce_info(self, recipe: CubeRecipeDTO) -> Tuple[str, str, str, str]:
        """Returns (canonical_tag, localized_family, mod_or_output_key, resolved_property_text)."""
        raw = recipe.get("raw_row", {})
        repo = self.analyzer.repo
        mods = self.analyzer._row_mods(raw)

        for code, param, mn, mx in mods:
            lower = code.lower()
            if lower in self.analyzer._pierce_mods or lower.startswith("pierce-"):
                raw_prefix = self.analyzer._pierce_prefix_by_mod.get(lower, "")
                family = (resolve_localized_string(repo, raw_prefix) or raw_prefix) if raw_prefix else self.analyzer.resolver.label_from_template(
                    self.analyzer.resolver.resolve_property(code, param, mn, mx).get("resolved_text", "")
                ) or lower
                canonical_tag = slugify(raw_prefix or lower)
                prop_text = self.analyzer.resolver.resolve_property(code, param, mn, mx).get("resolved_text", "") or lower
                return canonical_tag, family or "Pierce", lower, prop_text

        out_base = self.analyzer.parse_token(raw.get("output", ""))[0]
        unique_row = self.analyzer.unique_items_by_name.get(out_base.casefold())
        if unique_row:
            raw_prefix = ""
            mod_code = ""
            props_text: List[str] = []
            for idx in range(1, 13):
                prop = unique_row.get(f"prop{idx}", "").strip()
                if not prop:
                    continue
                if "-affix" in prop.lower():
                    prefix_part = prop.split("-", 1)[0].strip()
                    mapped_mod = self.analyzer._pierce_prefix_to_mod.get(prefix_part.casefold(), "")
                    if mapped_mod:
                        mod_code = mapped_mod
                        raw_prefix = self.analyzer._pierce_prefix_by_mod.get(mapped_mod, prefix_part)
                resolved = self.analyzer.resolver.resolve_property(
                    prop,
                    unique_row.get(f"par{idx}", ""),
                    unique_row.get(f"min{idx}", ""),
                    unique_row.get(f"max{idx}", ""),
                ).get("resolved_text", "").strip()
                if (
                    resolved
                    and not resolved.startswith("Unknown property (")
                    and "Missing Affix" not in resolved
                    and resolved not in props_text
                ):
                    props_text.append(resolved)

            family = (resolve_localized_string(repo, raw_prefix) or raw_prefix) if raw_prefix else "Pierce"
            canonical_tag = slugify(raw_prefix or mod_code or out_base)
            return canonical_tag, family, out_base.casefold(), "; ".join(props_text) or self.analyzer.get_item_name(out_base)

        fallback_prop = raw.get("mod 1", "").strip() or out_base
        return "pierce", "Pierce", fallback_prop.lower(), self._property_text(fallback_prop, raw)

    def pierce_page(self) -> Dict[str, Any]:
        pierce_recipes = [
            recipe for recipe in self.raw_recipes
            if self.analyzer._is_pierce_row(recipe.get("raw_row", {}))
        ]
        grouped: Dict[Tuple[str, str, Tuple[str, ...], str], List[Tuple[CubeRecipeDTO, str]]] = {}
        for recipe in pierce_recipes:
            raw = recipe["raw_row"]
            canonical_tag, family, prop_key, prop_text = self._pierce_info(recipe)
            ingredient_key = tuple(
                raw.get(f"input {index}", "").strip()
                for index in range(2, 8)
                if raw.get(f"input {index}", "").strip() and raw.get(f"input {index}", "").strip() != "0"
            )
            grouped.setdefault((canonical_tag, family, ingredient_key, prop_key), []).append((recipe, prop_text))

        families = []
        filters_by_tag: Dict[str, str] = {}
        for (canonical_tag, family, ingredient_key, prop_key), items in grouped.items():
            first, prop_text = items[0]
            recipes = [item[0] for item in items]
            item_types = sorted({self._base_name(self._token_base(r.get("raw_row", {}).get("input 1", ""))) for r in recipes})
            filters_by_tag.setdefault(canonical_tag, family)
            families.append(
                {
                    "id": canonical_tag or slugify(prop_key or "pierce"),
                    "family": family or "Pierce",
                    "filter_tags": canonical_tag or "pierce",
                    "property": prop_text,
                    "ingredients": [self.analyzer.resolve_token(token) for token in ingredient_key],
                    "item_types": item_types,
                    "result": first["outputs"][0] if first["outputs"] else "",
                    "search_text": " ".join([family, prop_text, " ".join(item_types), " ".join(first["inputs"]), " ".join(first["outputs"])]),
                }
            )
        filters = [
            {
                "value": tag,
                "label": label,
                "count": len([row for row in families if row["filter_tags"] == tag]),
            }
            for tag, label in sorted(filters_by_tag.items(), key=lambda entry: (entry[1], entry[0]))
        ]
        return {"families": sorted(families, key=lambda row: (row["family"], row["property"])), "filters": filters}

    def reforge_upgrade_page(self) -> Dict[str, Any]:
        section_defs = [
            ("upgrades", "Tier Upgrades", ["item-upgrades"]),
            ("sockets", "Socketing and Larzuk", ["socketing", "reforging"]),
            ("reforge", "Reforge and State Changes", ["reforging"]),
            ("repair", "Repair and Quantity Augments", ["repair"]),
        ]
        sections = []
        for section_id, title, group_ids in section_defs:
            rows = []
            for group_id in group_ids:
                for recipe in self.group_by_id.get(group_id, {}).get("recipes", []):
                    raw = recipe.get("raw_row", {})
                    if section_id in {"sockets", "reforge"} and self.analyzer._is_augment_row(raw):
                        continue
                    is_sock = self.analyzer._is_socketing_row(raw)
                    if section_id == "sockets" and not is_sock:
                        continue
                    if section_id == "reforge" and is_sock:
                        continue
                    rows.append(self._display_recipe_row(recipe))
            if rows:
                sections.append({"id": section_id, "title": title, "filter_tags": section_id, "rows": rows})

        augment_rows = self._augment_rows()
        if augment_rows:
            sections.append({"id": "augments", "title": "Augments", "filter_tags": "augments", "rows": augment_rows})
        return {
            "sections": sections,
            "filters": [{"value": section["id"], "label": section["title"], "count": len(section["rows"])} for section in sections],
        }

    def materials_page(self) -> Dict[str, Any]:
        section_map = [
            ("rune-ladders", "Rune Ladders", ["runes"]),
            ("materials", "Materials and Conversions", ["materials", "stacking", "tablets"]),
            ("quests", "Quest, Reward, and Utility", ["portals-quests", "charms-jewels-rewards", "general"]),
        ]
        sections = []
        for section_id, title, group_ids in section_map:
            rows = []
            for group_id in group_ids:
                for recipe in self.group_by_id.get(group_id, {}).get("recipes", []):
                    rows.append(self._display_recipe_row(recipe))
            if rows:
                sections.append({"id": section_id, "title": title, "filter_tags": section_id, "rows": rows})
        return {
            "sections": sections,
            "filters": [{"value": section["id"], "label": section["title"], "count": len(section["rows"])} for section in sections],
        }

    def all_page(self, crafting, corruptions, pierce, reforge, materials) -> Dict[str, Any]:
        rows: List[Dict[str, Any]] = []

        def add_row(
            system: str,
            filter_tag: str,
            category: str,
            recipe: str,
            ingredients: List[str],
            results: List[str],
            details: List[str],
            search_parts: List[str],
        ) -> None:
            rows.append(
                {
                    "system": system,
                    "filter_tags": filter_tag,
                    "category": category,
                    "recipe": recipe,
                    "ingredients": ingredients,
                    "results": results,
                    "details": details,
                    "search_text": " ".join(
                        [system, category, recipe] + ingredients + results + details + search_parts
                    ),
                }
            )

        for section in crafting["sections"]:
            for row in section["rows"]:
                for variant in row["variants"]:
                    variant_label = variant["variant"]
                    recipe = row["item_type"]
                    if variant_label and variant_label != "standard":
                        recipe = f"{recipe} - {variant_label}"
                    add_row(
                        "Crafting",
                        "crafting",
                        section["title"],
                        recipe,
                        variant["ingredients"],
                        [variant["output"]],
                        variant["fixed_properties"],
                        [row.get("search_text", ""), variant_label],
                    )

        for section in corruptions.get("sections", []):
            filter_tag = section["id"]
            category = section["title"]
            for summary in section["summaries"]:
                details = [
                    " ".join([outcome.get("chance", ""), outcome.get("label", ""), outcome.get("detail", ""), outcome.get("range", "")]).strip()
                    for outcome in summary.get("outcomes", [])
                ]
                add_row(
                    "Corruptions",
                    "corruptions",
                    category,
                    summary["title"],
                    summary.get("inputs", []),
                    [f"{len(summary.get('outcomes', []))} possible outcomes"],
                    details,
                    [summary.get("search_text", ""), filter_tag],
                )

        for row in pierce["families"]:
            add_row(
                "Pierce",
                "pierce",
                row["family"],
                row["property"],
                row["ingredients"],
                [row["result"]],
                [", ".join(row["item_types"])],
                [row.get("search_text", "")],
            )

        for page, system, filter_tag in ((reforge, "Reforge and Upgrade", "reforge-upgrade"), (materials, "Runes and Materials", "materials")):
            for section in page["sections"]:
                for row in section["rows"]:
                    add_row(
                        system,
                        filter_tag,
                        section["title"],
                        row["description"],
                        row["ingredients"],
                        row["results"],
                        [],
                        [row.get("search_text", "")],
                    )

        filters = [
            {"value": "crafting", "label": "Crafting", "count": len([row for row in rows if row["filter_tags"] == "crafting"])},
            {"value": "corruptions", "label": "Corruptions", "count": len([row for row in rows if row["filter_tags"] == "corruptions"])},
            {"value": "pierce", "label": "Pierce", "count": len([row for row in rows if row["filter_tags"] == "pierce"])},
            {"value": "reforge-upgrade", "label": "Reforge and Upgrade", "count": len([row for row in rows if row["filter_tags"] == "reforge-upgrade"])},
            {"value": "materials", "label": "Runes and Materials", "count": len([row for row in rows if row["filter_tags"] == "materials"])},
        ]
        return {"rows": rows, "filters": filters}

    def raw_page(self) -> Dict[str, Any]:
        rows = []
        for index, recipe in enumerate(self.raw_recipes, start=1):
            raw = recipe.get("raw_row", {})
            rows.append(
                {
                    "row": index,
                    "description": recipe["description"],
                    "status": recipe.get("status", "unchanged"),
                    "inputs": recipe["inputs"],
                    "outputs": recipe["outputs"],
                    "raw_inputs": [raw.get(f"input {i}", "").strip() for i in range(1, 8) if raw.get(f"input {i}", "").strip()],
                    "raw_outputs": [raw.get(column, "").strip() for column in ("output", "output 2", "output 3", "output b", "output c") if raw.get(column, "").strip()],
                    "search_text": " ".join([recipe["description"], " ".join(recipe["inputs"]), " ".join(recipe["outputs"])]),
                }
            )
        return {"rows": rows}

    def _display_recipe_row(self, recipe: CubeRecipeDTO) -> Dict[str, Any]:
        title = self.analyzer.display_title(recipe)
        return {
            "description": title,
            "ingredients": recipe.get("inputs", []),
            "results": recipe.get("outputs", []),
            "status": recipe.get("status", "unchanged"),
            "search_text": " ".join([title, " ".join(recipe.get("inputs", [])), " ".join(recipe.get("outputs", []))]),
        }

    def _augment_rows(self) -> List[Dict[str, Any]]:
        grouped: Dict[Tuple[Tuple[str, ...], Tuple[Tuple[str, str, str], ...]], List[CubeRecipeDTO]] = {}
        for recipe in self.raw_recipes:
            raw = recipe.get("raw_row", {})
            if not self.analyzer._is_augment_row(raw):
                continue
            mods = tuple(
                (raw.get(f"mod {index}", "").strip(), raw.get(f"mod {index} min", "").strip(), raw.get(f"mod {index} max", "").strip())
                for index in range(1, 6)
                if raw.get(f"mod {index}", "").strip()
            )
            rest = tuple(
                raw.get(f"input {index}", "").strip()
                for index in range(2, 8)
                if raw.get(f"input {index}", "").strip() and raw.get(f"input {index}", "").strip() != "0"
            )
            grouped.setdefault((rest, mods), []).append(recipe)

        rows = []
        for (rest, _mods), recipes in grouped.items():
            first = recipes[0]
            item_types = sorted({self._base_name(self._token_base(r["raw_row"].get("input 1", ""))) for r in recipes})
            title = self._augment_title(first, item_types)
            fixed_props = self._fixed_properties(first["raw_row"])
            ingredients = [self._join_labels(item_types, connector="or")] + [self.analyzer.resolve_token(token) for token in rest]
            rows.append(
                {
                    "description": title,
                    "ingredients": ingredients,
                    "results": fixed_props,
                    "status": first.get("status", "unchanged"),
                    "search_text": " ".join([title, " ".join(item_types), " ".join(ingredients), " ".join(fixed_props)]),
                }
            )
        return sorted(rows, key=lambda row: row["description"])

    def _augment_title(self, recipe: CubeRecipeDTO, item_types: List[str]) -> str:
        raw = recipe.get("raw_row", {})
        labels: List[str] = []
        for code, param, mn, mx in self.analyzer._row_mods(raw):
            if code.lower().startswith("augmented"):
                continue
            resolved = self.analyzer.resolver.resolve_property(code, param, mn, mx).get("resolved_text", "").strip()
            if not resolved or resolved.startswith("Unknown property ("):
                continue
            label = PropertyResolverService.label_from_template(resolved) or resolved
            if label and label not in labels:
                labels.append(label)
        if labels:
            return ", ".join(labels)
        return f"Augment {self._join_labels(item_types, connector='or')}"

    def _craft_source(self, raw: Dict[str, str]) -> str:
        return self.analyzer._craft_source_for_row(raw)

    def _craft_family(self, raw: Dict[str, str], description: str) -> str:
        return self.analyzer._craft_family_name(raw.get("input 2", ""), description, raw)

    def _craft_variant_name(self, raw: Dict[str, str]) -> str:
        input_parts = self._token_parts(raw.get("input 1", ""))
        state_parts = [
            self.analyzer.state_label(part)
            for part in input_parts[1:]
            if part in {"noe", "eth"}
        ]
        if "ethereal" in self.analyzer._row_mod_codes(raw) and "eth" not in input_parts[1:]:
            state_parts.append(f"adds {self.analyzer.state_label('eth')}")
        return ", ".join(state_parts) if state_parts else "standard"

    def _craft_summary(self, source: str, family: str) -> str:
        source_text = {
            "Classic": "Classic jewel, rune, and perfect gem recipe.",
            "Tablet": "Tablet shortcut recipe using the matching crafting tablet.",
            "Ascended": "Ascended gem recipe with stronger endgame materials.",
        }.get(source, "Crafting recipe.")
        return f"{source_text} Shows fixed {family} properties by item type."

    def _ingredient_labels(self, raw: Dict[str, str], start: int = 1) -> List[str]:
        return [
            self.analyzer.resolve_token(raw.get(f"input {index}", "").strip())
            for index in range(start, 8)
            if raw.get(f"input {index}", "").strip() and raw.get(f"input {index}", "").strip() != "0"
        ]

    def _fixed_properties(self, raw: Dict[str, str]) -> List[str]:
        return self.analyzer._resolve_output_modifiers(raw)

    def _property_text(self, prop: str, raw: Dict[str, str]) -> str:
        if not prop:
            return ""
        resolved = self.analyzer.resolver.resolve_property(
            prop,
            raw.get("mod 1 param", ""),
            raw.get("mod 1 min", ""),
            raw.get("mod 1 max", ""),
        ).get("resolved_text", "")
        if resolved and not resolved.startswith("Unknown property ("):
            return resolved
        return prop

    def _token_base(self, token: str) -> str:
        return self.analyzer.parse_token(token)[0]

    @staticmethod
    def _token_parts(token: str) -> List[str]:
        return CubeAnalyzerService._raw_token_parts(token)

    def _base_name(self, code: str) -> str:
        return self.analyzer._display_base_names([self.analyzer.get_item_name(code)])[0] if code else ""

    @staticmethod
    def _join_labels(labels: List[str], connector: str = "and") -> str:
        labels = [label for label in labels if label]
        if not labels:
            return ""
        if len(labels) == 1:
            return labels[0]
        return f"{', '.join(labels[:-1])} {connector} {labels[-1]}"
