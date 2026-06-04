from __future__ import annotations
import re
from typing import List, Dict, Optional, Any, Tuple
from d2lib.repository import D2Repository, D2RepositoryProtocol
from d2lib.models import CubeRecipeDTO, CubeRecipeGroupDTO
from d2lib.services.resolver import PropertyResolverService
from d2lib.utils import slugify
from d2lib.services.base import _status_for_row

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
        "Removed Retail Recipes": {
            "id": "removed-retail",
            "order": 900,
            "action": "See retail recipes not present in BK",
            "summary": "Retail cube recipes that are absent from the BK enabled recipe set.",
        },
    }

    def __init__(self, repo: D2RepositoryProtocol, retail_repo: Optional[D2RepositoryProtocol] = None):
        self.repo = repo
        self.retail_repo = retail_repo
        self.resolver = PropertyResolverService(repo)
        self.armor = {row['code']: row for row in repo.get_excel_table('armor')}
        self.weapons = {row['code']: row for row in repo.get_excel_table('weapons')}
        self.misc = {row['code']: row for row in repo.get_excel_table('misc')}
        self.item_types = {row['Code']: row for row in repo.get_excel_table('itemtypes')}
        self.retail_recipe_rows = {
            row.get('description', '').strip().lower(): row
            for row in retail_repo.get_excel_table('cubemain')
            if row.get('description') and self._is_enabled_recipe_row(row)
        } if retail_repo else {}

        # Prefixes and Suffixes use row index as ID
        prefix_data = repo.get_excel_table('magicprefix')
        self.prefixes = {str(i): row for i, row in enumerate(prefix_data)}

        suffix_data = repo.get_excel_table('magicsuffix')
        self.suffixes = {str(i): row for i, row in enumerate(suffix_data)}

    def get_item_name(self, code: str) -> str:
        if not code: return ""
        code = code.strip()
        code_lower = code.lower()
        if code_lower == "usetype": return "Input Item Type"
        if code_lower == "useitem": return "Input Item"
        if code_lower == "any": return "Any Item"

        item = self.armor.get(code) or self.weapons.get(code) or self.misc.get(code)
        if item:
            name = self.repo.get_string(item.get('namestr', '').strip() or item.get('name', '').strip())
            return name or code

        # Check item types
        it = self.item_types.get(code)
        if it:
            return self.repo.get_string(it.get('ItemType', '').strip()) or code

        return code

    def resolve_token(self, token: str) -> str:
        if not token: return ""
        token = token.strip().strip('"')

        # Handle quantity: "code,qty=3"
        qty = ""
        if ",qty=" in token:
            parts = token.split(",qty=", 1)
            token = parts[0]
            qty = f" (Qty: {parts[1]})"

        # Handle complex codes: "amu,mag" or "rin,mag,pre=372"
        parts = token.split(',')
        base_code = parts[0]
        name = self.get_item_name(base_code)

        qualities = {
            "low": "Low Quality", "nor": "Normal", "hi": "Superior", "mag": "Magic",
            "set": "Set", "uni": "Unique", "rar": "Rare", "ora": "Crafted", "crf": "Crafted", "tmp": "Tempered"
        }

        mods = []
        for p in parts[1:]:
            p = p.strip().lower()
            if p in qualities:
                mods.append(qualities[p])
            elif p.startswith("pre="):
                val = p.split("=")[1]
                pre = self.prefixes.get(val)
                pre_name = self.repo.get_string(pre.get('Name', '')) if pre else val
                mods.append(f"Prefix: {pre_name} ({val})")
            elif p.startswith("suf="):
                val = p.split("=")[1]
                suf = self.suffixes.get(val)
                suf_name = self.repo.get_string(suf.get('Name', '')) if suf else val
                mods.append(f"Suffix: {suf_name} ({val})")
            else:
                mods.append(p)

        res = name
        if mods:
            res += f" ({', '.join(mods)})"
        return f"{res}{qty}"

    def resolve_output(self, out: str, mod_str: str = "", mod_val: str = "") -> str:
        if not out: return ""
        res = self.resolve_token(out)
        qualities = {"low": "Low Quality", "nor": "Normal", "hi": "Superior", "mag": "Magic", "set": "Set", "uni": "Unique", "rar": "Rare", "ora": "Crafted", "crf": "Crafted", "tmp": "Tempered"}
        extra_mods = []
        if mod_str:
            parts = mod_str.split(',')
            for p in parts:
                p = p.strip().lower()
                if p in qualities: extra_mods.append(qualities[p])
                elif p == "pre":
                    pre = self.prefixes.get(mod_val)
                    pre_name = self.repo.get_string(pre.get('Name', '')) if pre else mod_val
                    extra_mods.append(f"Prefix: {pre_name} ({mod_val})")
                elif p == "suf":
                    suf = self.suffixes.get(mod_val)
                    suf_name = self.repo.get_string(suf.get('Name', '')) if suf else mod_val
                    extra_mods.append(f"Suffix: {suf_name} ({mod_val})")
                else: extra_mods.append(p)
        if extra_mods: res += f" [Extra: {', '.join(extra_mods)}]"
        return res

    def analyze_recipe(self, row: Dict[str, str], status: Optional[str] = None) -> CubeRecipeDTO:
        desc = row.get('description', 'Unknown Recipe').strip()
        enabled = row.get('enabled', '1').strip() == '1'
        actual_inputs = []
        for i in range(1, 8):
            val = row.get(f'input {i}', '').strip()
            if val and val != '0': actual_inputs.append(self.resolve_token(val))
        outputs = []
        output_slots = [
            ("output", "mod 1", "mod 1 param"),
            ("output 2", "mod 2", "mod 2 param"),
            ("output 3", "mod 3", "mod 3 param"),
            ("output b", "b mod 1", "b mod 1 param"),
            ("output c", "c mod 1", "c mod 1 param"),
        ]
        for output_column, mod_column, mod_param_column in output_slots:
            out = row.get(output_column, '').strip()
            if out and out != '0':
                mod_str = row.get(mod_column, '').strip()
                mod_val = row.get(mod_param_column, '').strip()
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

            if group_name not in groups: groups[group_name] = []
            groups[group_name].append(r)

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
        if group_name == "Classic Crafting":
            return self._condense_classic_crafting(recipes)
        if group_name == "Item Upgrades":
            return self._condense_item_upgrades(recipes)
        if group_name == "Socketing & Sockets":
            return self._condense_socketing_recipes(recipes)
        if group_name == "Item Reforging & Cosmetics":
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
            if len(rows) == 1:
                condensed.append(self._classic_craft_display_recipe(rows))
                continue
            condensed.append(self._classic_craft_display_recipe(rows))
        return condensed

    def _classic_craft_key(self, recipe: CubeRecipeDTO) -> Optional[Tuple[Any, ...]]:
        raw = recipe.get("raw_row", {})
        output = raw.get("output", "").strip()
        if output.lower() != "usetype,crf":
            return None

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

        display_description = f"{family} Craft"
        if len(self._classic_craft_base_names(rows)) == 1:
            display_description = f"{family} {self._classic_craft_base_names(rows)[0]} Craft"

        return {
            "id": display_description,
            "description": display_description,
            "enabled": True,
            "status": first.get("status", "unchanged"),
            "inputs": inputs,
            "outputs": outputs,
            "raw_row": raw,
        }

    def _craft_family_name(self, tablet_code: str, description: str = "", raw: Optional[Dict[str, str]] = None) -> str:
        code = tablet_code.strip().lower()
        explicit_names = {
            "bct": "Blood",
            "cct": "Caster",
            "pct": "Hit Power",
            "sct": "Safety",
        }
        if code in explicit_names:
            return explicit_names[code]

        desc = description.lower()
        for family in ("blood", "caster", "safety", "hit power"):
            if f"-> {family}" in desc or f"to {family}" in desc:
                return family.title()

        if raw:
            first_mod = raw.get("mod 1", "").strip().lower()
            if first_mod == "lifesteal":
                return "Blood"
            if first_mod in {"regen-mana", "mana-kill", "allskills", "cast1"}:
                return "Caster"
            if first_mod in {"red-dmg", "red-mag"}:
                return "Safety"
            if first_mod == "gethit-skill":
                return "Hit Power"

        item = self.misc.get(tablet_code.strip())
        name = item.get("name", "").strip() if item else self.get_item_name(tablet_code)
        for suffix in (" Crafting Tablet", " Tablet"):
            if name.endswith(suffix):
                return name[: -len(suffix)]
        return name or "Crafting"

    def _classic_craft_base_label(self, rows: List[CubeRecipeDTO]) -> str:
        base_names = self._classic_craft_base_names(rows)
        quality_names = self._classic_craft_quality_names(rows)
        eth_states = self._classic_craft_eth_states(rows)

        quality = " ".join(quality_names) if quality_names else ""
        if len(base_names) == 1:
            label = " ".join(part for part in (quality, base_names[0]) if part)
        else:
            label = " ".join(part for part in (quality, "Items") if part)
            label += f": {', '.join(base_names)}"

        if eth_states == {"eth"}:
            label += " (ethereal)"
        elif eth_states == {"noe"}:
            label += " (non-ethereal)"
        return label

    def _classic_craft_base_names(self, rows: List[CubeRecipeDTO]) -> List[str]:
        names: List[str] = []
        for recipe in rows:
            token = recipe.get("raw_row", {}).get("input 1", "").strip()
            if not token:
                continue
            base_code = token.split(",", 1)[0]
            name = self.get_item_name(base_code)
            if name and name not in names:
                names.append(name)
        return names

    def _classic_craft_quality_names(self, rows: List[CubeRecipeDTO]) -> List[str]:
        quality_labels = {
            "low": "Low Quality",
            "nor": "Normal",
            "hi": "Superior",
            "mag": "Magic",
            "set": "Set",
            "uni": "Unique",
            "rar": "Rare",
            "ora": "Crafted",
            "crf": "Crafted",
            "tmp": "Tempered",
        }
        qualities: List[str] = []
        for recipe in rows:
            parts = recipe.get("raw_row", {}).get("input 1", "").strip().split(",")[1:]
            for part in parts:
                label = quality_labels.get(part.strip().lower())
                if label and label not in qualities:
                    qualities.append(label)
        return qualities

    def _classic_craft_eth_states(self, rows: List[CubeRecipeDTO]) -> set:
        states = set()
        for recipe in rows:
            parts = recipe.get("raw_row", {}).get("input 1", "").strip().split(",")[1:]
            for part in parts:
                value = part.strip().lower()
                if value in {"eth", "noe"}:
                    states.add(value)
        return states

    @staticmethod
    def _classic_craft_extra_inputs(raw: Dict[str, str]) -> List[str]:
        return [
            raw.get(f"input {index}", "").strip()
            for index in range(2, 8)
            if raw.get(f"input {index}", "").strip() and raw.get(f"input {index}", "").strip() != "0"
        ]

    def _classic_craft_result(self, raw: Dict[str, str]) -> str:
        output = raw.get("output", "").strip()
        if output.lower() == "usetype,crf":
            return "Input Item Type (Crafted)"
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
            if text and text not in modifiers:
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
        output = raw.get("output", "").strip().lower()
        if output not in {"useitem,mod,exc", "useitem,mod,eli"}:
            return None

        parts = self._raw_token_parts(raw.get("input 1", ""))
        if len(parts) < 3 or parts[1] not in {"bas", "exc"}:
            return None

        extra_inputs = tuple(
            raw.get(f"input {index}", "").strip()
            for index in range(2, 8)
            if raw.get(f"input {index}", "").strip() and raw.get(f"input {index}", "").strip() != "0"
        )
        modifiers = tuple(
            raw.get(f"mod {index}", "").strip()
            for index in range(1, 6)
            if raw.get(f"mod {index}", "").strip()
        )
        return (recipe.get("status", "unchanged"), output, extra_inputs, modifiers)

    def _item_upgrade_display_recipe(self, rows: List[CubeRecipeDTO]) -> CubeRecipeDTO:
        first = rows[0]
        raw = first.get("raw_row", {})
        output = raw.get("output", "").strip().lower()
        from_tier = "Normal" if output == "useitem,mod,exc" else "Exceptional"
        to_tier = "Exceptional" if output == "useitem,mod,exc" else "Elite"
        qualities = self._quality_names_for_rows(rows)
        bases = self._base_names_for_rows(rows)
        quality_label = self._join_labels(qualities, slash=True)
        base_label = self._join_labels(self._display_base_names(bases), connector="or")
        subject = " ".join(part for part in (from_tier, quality_label, base_label) if part)

        extra_inputs = [
            self.resolve_token(raw.get(f"input {index}", "").strip())
            for index in range(2, 8)
            if raw.get(f"input {index}", "").strip() and raw.get(f"input {index}", "").strip() != "0"
        ]

        return {
            "id": f"{from_tier} to {to_tier} {quality_label} Gear",
            "description": f"{from_tier} to {to_tier} {quality_label} Gear",
            "enabled": True,
            "status": first.get("status", "unchanged"),
            "inputs": [subject] + extra_inputs,
            "outputs": [f"{to_tier} version of input item"],
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
        if raw.get("input 2", "").strip().lower() != "lmr":
            return None
        if any(raw.get(f"input {index}", "").strip() for index in range(3, 8)):
            return None

        parts = self._raw_token_parts(raw.get("input 1", ""))
        if not parts:
            return None
        return (recipe.get("status", "unchanged"), raw.get("output", "").strip().lower(), raw.get("mod 1", "").strip().lower(), parts[0])

    def _socket_reforge_display_recipe(self, rows: List[CubeRecipeDTO]) -> CubeRecipeDTO:
        first = rows[0]
        raw = first.get("raw_row", {})
        bases = self._display_base_names(self._base_names_for_rows(rows))
        qualities = self._quality_names_for_rows(rows)
        state_labels = self._state_labels_for_rows(rows)
        base_label = self._join_labels(bases, connector="or")
        quality_label = self._join_labels(qualities, slash=True)
        state_label = f" ({', '.join(state_labels)})" if state_labels else ""
        item_label = " ".join(part for part in (quality_label, base_label) if part) + state_label

        return {
            "id": f"Add sockets to {base_label}",
            "description": f"Add sockets to {base_label}",
            "enabled": True,
            "status": first.get("status", "unchanged"),
            "inputs": [item_label, self.resolve_token(raw.get("input 2", ""))],
            "outputs": ["Input Item (socketed)"],
            "raw_row": raw,
        }

    @staticmethod
    def _raw_token_parts(token: str) -> List[str]:
        return [part.strip().lower() for part in token.strip().strip('"').split(",") if part.strip()]

    def _base_names_for_rows(self, rows: List[CubeRecipeDTO]) -> List[str]:
        names: List[str] = []
        for recipe in rows:
            parts = self._raw_token_parts(recipe.get("raw_row", {}).get("input 1", ""))
            if not parts:
                continue
            name = self.get_item_name(parts[0])
            if name and name not in names:
                names.append(name)
        return names

    def _quality_names_for_rows(self, rows: List[CubeRecipeDTO]) -> List[str]:
        order = ["low", "nor", "hiq", "mag", "rar", "set", "uni", "crf", "tmp"]
        labels = {
            "low": "Low Quality",
            "nor": "Normal",
            "hiq": "Superior",
            "mag": "Magic",
            "rar": "Rare",
            "set": "Set",
            "uni": "Unique",
            "crf": "Crafted",
            "tmp": "Tempered",
        }
        seen = set()
        for recipe in rows:
            parts = self._raw_token_parts(recipe.get("raw_row", {}).get("input 1", ""))[1:]
            for part in parts:
                if part in labels:
                    seen.add(part)
        return [labels[key] for key in order if key in seen]

    def _state_labels_for_rows(self, rows: List[CubeRecipeDTO]) -> List[str]:
        order = [("noe", "non-ethereal"), ("eth", "ethereal"), ("nos", "unsocketed")]
        seen = set()
        for recipe in rows:
            parts = self._raw_token_parts(recipe.get("raw_row", {}).get("input 1", ""))[1:]
            for part in parts:
                if part in {"noe", "eth", "nos"}:
                    seen.add(part)
        return [label for key, label in order if key in seen]

    @staticmethod
    def _display_base_names(names: List[str]) -> List[str]:
        replacements = {
            "Any Armor": "Armor",
            "Any Shield": "Shield",
            "Merc Equip": "Helm",
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

    def _recipe_group_name(self, recipe: CubeRecipeDTO) -> str:
        if recipe.get("status") == "removed":
            return "Removed Retail Recipes"

        desc = recipe["description"].lower()
        haystack = " ".join([desc] + recipe.get("inputs", []) + recipe.get("outputs", [])).lower()

        if "corrupt" in haystack:
            return "Corruption Recipes"
        if any(token in haystack for token in ("socket", "sockets", "unsocket", "clear sockets")):
            return "Socketing & Sockets"
        if any(token in desc for token in ("upgrade", "to exceptional", "to elite", "upped", "downgrade")):
            return "Item Upgrades"
        if "->" in desc and any(token in desc for token in (" exceptional ", " elite ", " exceptional", " elite")):
            return "Item Upgrades"
        if "ascended" in haystack or "ascension" in haystack:
            return "Ascended Crafting"
        if any(token in desc for token in ("incendiary", "magnetic", "virulent", "gelid", "mystical", "breaching")):
            return "Pierce Amulet Crafting"
        if any(token in desc for token in ("blood ", " caster ", " safety ", " hit power ", "bloody")):
            return "Classic Crafting"
        if "tablet" in haystack:
            return "Crafting Tablets"
        if "recharge" in desc or "repair" in desc or "replenish" in desc:
            return "Repair & Recharge"
        if any(token in desc for token in ("chipped", "flawed", "standard", "flawless", "perfect", "essence", "brick", "sigil")):
            return "Material Upgrades & Conversions"
        if any(token in desc for token in ("charm", "jewel", "annihilus", "hellfire torch", "gheed", "tarnhelm", "gull dagger")):
            return "Charm, Jewel & Reward Recipes"
        if self._looks_like_reforge_recipe(desc):
            return "Item Reforging & Cosmetics"
        if any(token in desc for token in ("stack", "unstack", "quantity", "arrows", "bolts", "potion")):
            return "Stacking & Utility"
        if any(token in desc for token in ("portal", "cow", "horadric staff", "uber", "pandemonium", "key")):
            return "Portals & Quest Recipes"
        if "rune" in haystack:
            return "Rune Transmutation"
        return "General Recipes"

    def _corruption_summaries(self, recipes: List[CubeRecipeDTO]) -> List[Dict[str, Any]]:
        grouped: Dict[Tuple[str, ...], List[CubeRecipeDTO]] = {}
        display_inputs: Dict[Tuple[str, ...], List[str]] = {}
        for recipe in recipes:
            value = self._to_int(recipe.get("raw_row", {}).get("value"))
            description = recipe.get("description", "").strip()
            if not recipe.get("inputs") or not description or "---" in description or value <= 0:
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
            inputs = display_inputs[key]
            summaries.append(
                {
                    "id": slugify(" ".join(inputs)),
                    "inputs": list(inputs),
                    "title": " + ".join(inputs),
                    "material": inputs[-1] if len(inputs) > 1 else "",
                    "outcomes": outcomes,
                    "search_text": " ".join(inputs) + " " + " ".join(outcome["label"] for outcome in outcomes),
                }
            )
        return sorted(summaries, key=lambda summary: (summary["material"], summary["title"]))

    def _corruption_raw_input_key(self, recipe: CubeRecipeDTO) -> Tuple[str, ...]:
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
        explicit = {
            "2han": ["weap"],
        }
        ancestors: List[str] = explicit.get(item_type, []).copy()
        seen = set(ancestors)

        def walk(code: str) -> None:
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
        return ancestors

    @staticmethod
    def _is_parent_corruption_outcome(recipe: CubeRecipeDTO) -> bool:
        return recipe.get("description", "").strip().lower() == "brick"

    def _is_parent_only_corruption_group(
        self,
        key: Tuple[str, ...],
        rows: List[CubeRecipeDTO],
        grouped: Dict[Tuple[str, ...], List[CubeRecipeDTO]],
    ) -> bool:
        has_specific_outcome = any(
            self._to_int(recipe.get("raw_row", {}).get("value")) > 0
            and recipe.get("description", "").strip().lower() != "brick"
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
                recipe.get("raw_row", {}).get("mod 2", "").strip() == "sock"
                and self._to_int(recipe.get("raw_row", {}).get("value")) > 0
                for recipe in candidate_rows
            ):
                return True
        return False

    def _corruption_outcomes(self, rows: List[CubeRecipeDTO]) -> List[Dict[str, Any]]:
        sorted_rows = sorted(rows, key=lambda recipe: (self._to_int(recipe["raw_row"].get("value")), recipe["description"]))
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

    def _corruption_outcome_label(self, recipe: CubeRecipeDTO) -> str:
        description = recipe.get("description", "").strip()
        raw = recipe.get("raw_row", {})
        mod_code = raw.get("mod 2", "").strip()
        if description.lower() == "brick":
            return "Brick"
        if mod_code == "sock":
            sockets_min = raw.get("mod 2 min", "").strip()
            sockets_max = raw.get("mod 2 max", "").strip()
            if sockets_min and sockets_min == sockets_max:
                return f"Add {sockets_min} socket{'s' if sockets_min != '1' else ''}"
            if sockets_min and sockets_max:
                return f"Add {sockets_min}-{sockets_max} sockets"
            return "Add sockets"
        return description

    def _corruption_outcome_detail(self, recipe: CubeRecipeDTO) -> str:
        raw = recipe.get("raw_row", {})
        mod_code = raw.get("mod 2", "").strip()
        if not mod_code or mod_code == "sock":
            if recipe.get("description", "").strip().lower() == "brick":
                return "The item bricks and produces the listed brick/material output."
            return ""
        resolved = self.resolver.resolve_property(
            mod_code,
            raw.get("mod 2 param", ""),
            raw.get("mod 2 min", ""),
            raw.get("mod 2 max", ""),
        )
        return resolved.get("resolved_text", "")

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
        has_input = False
        for column in input_columns + output_columns:
            value = row.get(column, "").strip()
            if value and value != "0" and column in input_columns:
                has_input = True
                break
        has_output = False
        for column in output_columns:
            value = row.get(column, "").strip()
            if value and value != "0":
                has_output = True
                break
        return has_input and has_output

    @staticmethod
    def _looks_like_reforge_recipe(desc: str) -> bool:
        if any(token in desc for token in (" eth", " sup", " inf", "black", "white", "transmogify", "flask")):
            return True
        normalized = re.sub(r"\s+", " ", desc.strip().lower())
        base_terms = {
            "armor", "belt", "boots", "circ", "gloves", "helm", "shield", "weapon",
            "throwing axes", "throwing javelins", "throwing knives", "block bows",
            "block charms", "block jewels",
        }
        return normalized in base_terms

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
        recipes_data = self.repo.get_excel_table('cubemain')
        recipes = [
            self.analyze_recipe(row)
            for row in recipes_data
            if self._is_enabled_recipe_row(row)
        ]

        if include_removed and self.retail_repo:
            bk_recipe_keys = {
                row.get('description', '').strip().lower()
                for row in recipes_data
                if row.get('description') and self._is_enabled_recipe_row(row)
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
            "summary": "Rune ladders, gem conversions, standards, bricks, sigils, keys, and utility recipes.",
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

    QUALITY_LABELS = {
        "low": "Low Quality",
        "nor": "Normal",
        "hiq": "Superior",
        "mag": "Magic",
        "rar": "Rare",
        "set": "Set",
        "uni": "Unique",
        "crf": "Crafted",
        "ora": "Crafted",
        "tmp": "Tempered",
        "exc": "Exceptional",
        "bas": "Normal",
    }
    STATE_LABELS = {"noe": "non-ethereal", "eth": "ethereal", "nos": "unsocketed"}

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
        counts = {
            "raw_enabled_rows": len([recipe for recipe in self.raw_recipes if recipe.get("status") != "removed"]),
            "display_groups": len(self.groups),
            "craft_rows": sum(len(section["rows"]) for section in crafting["sections"]),
            "corruption_cards": len(corruptions["combined_summaries"]) + len(corruptions["standard_summaries"]) + len(corruptions["divine_summaries"]),
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
            recipe for recipe in self.raw_recipes
            if recipe.get("raw_row", {}).get("output", "").strip().lower() == "usetype,crf"
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
                variant_key = (
                    self._craft_variant_name(raw),
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
                        "variant": self._craft_variant_name(raw),
                        "ingredients": self._ingredient_labels(raw, start=2),
                        "output": "Input Item Type (Crafted)",
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
        summaries = list(corruption_group.get("corruption_summaries", []))
        divine = [summary for summary in summaries if any("Divine Standard" in inp for inp in summary.get("inputs", []))]
        standard = [summary for summary in summaries if summary not in divine]
        for summary in standard + divine:
            summary["filter_tags"] = "|".join(self._corruption_filter_tags(summary))
        standard = self._group_corruption_equivalent_summaries(standard)
        divine = self._group_corruption_equivalent_summaries(divine)
        combined, standard, divine = self._group_corruption_material_equivalent_summaries(standard, divine)
        combined = self._group_corruption_target_equivalent_summaries(combined)
        standard = self._group_corruption_target_equivalent_summaries(standard)
        divine = self._group_corruption_target_equivalent_summaries(divine)
        filter_defs = [
            ("charms", "Charms"),
            ("weapons", "Weapons"),
            ("wearables", "Armor & Wearables"),
            ("shields", "Shields"),
            ("jewelry", "Jewelry"),
            ("any-item", "Any Item"),
            ("named-uniques", "Named Uniques"),
        ]
        all_summaries = combined + standard + divine
        return {
            "combined_summaries": combined,
            "standard_summaries": standard,
            "divine_summaries": divine,
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
            family = RecipePresentationBuilder._corruption_target_family(inputs[0])
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
            target = RecipePresentationBuilder._combined_corruption_target_label([row["inputs"][0] for row in rows])
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
    def _corruption_target_family(target: str) -> str:
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
    def _combined_corruption_target_label(targets: List[str]) -> str:
        parsed = [RecipePresentationBuilder._corruption_target_label_and_rarities(target) for target in targets]
        order = {
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
        unique_parsed = []
        seen = set()
        for label, rarities in parsed:
            key = (label, rarities)
            if key not in seen:
                seen.add(key)
                unique_parsed.append((label, rarities))
        unique_parsed = sorted(unique_parsed, key=lambda item: (order.get(item[0].lower(), 999), item[0], item[1]))

        rarity_sets = {rarities for _label, rarities in unique_parsed}
        if len(rarity_sets) == 1:
            rarities = next(iter(rarity_sets))
            labels = ", ".join(label for label, _rarities in unique_parsed)
            return f"{labels} ({rarities})" if rarities else labels

        return " or ".join(
            f"{label} ({rarities})" if rarities else label
            for label, rarities in unique_parsed
        )

    @staticmethod
    def _corruption_target_label_and_rarities(target: str) -> Tuple[str, str]:
        match = re.match(r"^(?P<label>.+?) \((?P<rarities>[^)]+)\)$", target.strip())
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
    def _group_corruption_material_equivalent_summaries(standard: List[Dict[str, Any]], divine: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
        def signature(summary: Dict[str, Any]) -> Tuple[Any, ...]:
            inputs = summary.get("inputs", [])
            target = inputs[0] if inputs else summary.get("title", "")
            outcomes = tuple(
                (
                    outcome.get("label", ""),
                    outcome.get("detail", ""),
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
            first["inputs"] = [standard_summary["inputs"][0], "Standard of Heroes or The Divine Standard"]
            first["title"] = " + ".join(first["inputs"])
            first["id"] = slugify(" ".join(first["inputs"]))
            first["material"] = "Standard of Heroes or The Divine Standard"
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
    def _group_corruption_equivalent_summaries(summaries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        grouped: Dict[Tuple[Any, ...], List[Dict[str, Any]]] = {}
        passthrough: List[Dict[str, Any]] = []

        for summary in summaries:
            inputs = summary.get("inputs", [])
            if len(inputs) < 2:
                passthrough.append(summary)
                continue
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
        rarity_order = {"Crafted": 0, "Magic": 1, "Rare": 2, "Set": 3, "Unique": 4}
        for (_material, target_label, _filter_tags, _signature), rows in grouped.items():
            if len(rows) == 1:
                result.append(rows[0])
                continue

            rarities = []
            for row in rows:
                _, rarity = RecipePresentationBuilder._corruption_target_parts(row["inputs"][0])
                if rarity and rarity not in rarities:
                    rarities.append(rarity)
            rarities = sorted(rarities, key=lambda rarity: (rarity_order.get(rarity, 99), rarity))
            first = dict(rows[0])
            first["inputs"] = [f"{target_label} ({', '.join(rarities)})", rows[0]["inputs"][-1]]
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
        match = re.match(r"^(?P<label>.+?) \((?P<rarity>Crafted|Magic|Rare|Set|Unique)\)$", target.strip())
        if not match:
            return target, ""
        return match.group("label"), match.group("rarity")

    @staticmethod
    def _corruption_filter_tags(summary: Dict[str, Any]) -> List[str]:
        inputs = summary.get("inputs", [])
        target = inputs[0] if inputs else summary.get("title", "")
        normalized = target.lower()
        tags: List[str] = []

        def add(tag: str) -> None:
            if tag not in tags:
                tags.append(tag)

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
        if "merc equip" in normalized:
            add("merc-equip")
            add("wearables")
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
            "annihilus",
            "hellfire torch",
            "gheed's fortune",
            "2handed",
            "amulet",
            "any item",
            "any shield",
            "armor",
            "belt",
            "boots",
            "bow",
            "crossbow",
            "gloves",
            "merc equip",
            "ring",
            "weapon",
        )
        if not any(marker in normalized for marker in generic_markers):
            add("named-uniques")

        return tags or ["other"]

    def pierce_page(self) -> Dict[str, Any]:
        pierce_recipes = [
            recipe for recipe in self.raw_recipes
            if self._is_pierce_recipe(recipe)
        ]
        grouped: Dict[Tuple[str, Tuple[str, ...], str], List[CubeRecipeDTO]] = {}
        for recipe in pierce_recipes:
            raw = recipe["raw_row"]
            family = self._pierce_family(recipe["description"])
            ingredient_key = tuple(raw.get(f"input {index}", "").strip() for index in range(2, 8) if raw.get(f"input {index}", "").strip())
            prop = raw.get("mod 1", "").strip() or raw.get("output", "").strip()
            grouped.setdefault((family, ingredient_key, prop), []).append(recipe)

        families = []
        for (family, ingredient_key, prop), recipes in grouped.items():
            first = recipes[0]
            raw = first["raw_row"]
            item_types = sorted({self._base_name(self._token_base(recipe["raw_row"].get("input 1", ""))) for recipe in recipes})
            families.append(
                {
                    "id": slugify(family or prop or "pierce"),
                    "family": family or "Pierce",
                    "filter_tags": slugify(family or "Pierce"),
                    "property": self._property_text(prop, raw),
                    "ingredients": [self.analyzer.resolve_token(token) for token in ingredient_key],
                    "item_types": item_types,
                    "result": first["outputs"][0] if first["outputs"] else "",
                    "search_text": " ".join([family, prop, " ".join(item_types), " ".join(first["inputs"]), " ".join(first["outputs"])]),
                }
            )
        filters = [
            {
                "value": slugify(family),
                "label": family,
                "count": len([row for row in families if row["family"] == family]),
            }
            for family in sorted({row["family"] for row in families})
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
                    text = " ".join([recipe["description"], " ".join(recipe["inputs"]), " ".join(recipe["outputs"])]).lower()
                    if section_id == "sockets" and "socket" not in text:
                        continue
                    if section_id == "reforge" and "socket" in text:
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

        def add_row(system: str, filter_tag: str, category: str, recipe: str, ingredients: List[str], results: List[str], details: List[str], search_parts: List[str]) -> None:
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
                        [system, category, recipe]
                        + ingredients
                        + results
                        + details
                        + search_parts
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

        corruption_sections = [
            ("either-standard-corruptions", "Corruptions", "Standard of Heroes or The Divine Standard", corruptions["combined_summaries"]),
            ("standard-corruptions", "Corruptions", "Standard of Heroes", corruptions["standard_summaries"]),
            ("divine-corruptions", "Corruptions", "The Divine Standard", corruptions["divine_summaries"]),
        ]
        for filter_tag, system, category, summaries in corruption_sections:
            for summary in summaries:
                details = [
                    " ".join([outcome.get("chance", ""), outcome.get("label", ""), outcome.get("detail", ""), outcome.get("range", "")]).strip()
                    for outcome in summary.get("outcomes", [])
                ]
                add_row(
                    system,
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
        return {
            "description": recipe["description"],
            "ingredients": recipe.get("inputs", []),
            "results": recipe.get("outputs", []),
            "status": recipe.get("status", "unchanged"),
            "search_text": " ".join([recipe["description"], " ".join(recipe.get("inputs", [])), " ".join(recipe.get("outputs", []))]),
        }

    def _augment_rows(self) -> List[Dict[str, Any]]:
        grouped: Dict[Tuple[Tuple[str, ...], Tuple[Tuple[str, str, str], ...]], List[CubeRecipeDTO]] = {}
        for recipe in self.raw_recipes:
            raw = recipe["raw_row"]
            mods = tuple(
                (raw.get(f"mod {index}", "").strip(), raw.get(f"mod {index} min", "").strip(), raw.get(f"mod {index} max", "").strip())
                for index in range(1, 6)
                if raw.get(f"mod {index}", "").strip()
            )
            if not any(mod[0].startswith("augmented") for mod in mods) and "augment" not in recipe["description"].lower():
                continue
            rest = tuple(raw.get(f"input {index}", "").strip() for index in range(2, 8) if raw.get(f"input {index}", "").strip())
            grouped.setdefault((rest, mods), []).append(recipe)

        rows = []
        for (rest, mods), recipes in grouped.items():
            first = recipes[0]
            item_types = sorted({self._base_name(self._token_base(recipe["raw_row"].get("input 1", ""))) for recipe in recipes})
            rows.append(
                {
                    "description": self._augment_title(first, item_types),
                    "ingredients": [self._join_labels(item_types, connector="or")] + [self.analyzer.resolve_token(token) for token in rest],
                    "results": self._fixed_properties(first["raw_row"]),
                    "status": first.get("status", "unchanged"),
                    "search_text": " ".join([first["description"], " ".join(item_types)]),
                }
            )
        return sorted(rows, key=lambda row: row["description"])

    def _augment_title(self, recipe: CubeRecipeDTO, item_types: List[str]) -> str:
        desc = recipe["description"].lower()
        if "mf" in desc and "gf" in desc:
            return "Magic Find and Gold Find Augment"
        if "melee augment" in desc:
            return "Melee Augment"
        if "teleport" in desc:
            return "Teleport, Magic Find, and Gold Find Augment"
        if "repair augment" in desc:
            return "Repair Augment"
        return f"Augment {self._join_labels(item_types, connector='or')}"

    def _craft_source(self, raw: Dict[str, str]) -> str:
        desc = raw.get("description", "").lower()
        inputs = " ".join(raw.get(f"input {i}", "") for i in range(1, 8)).lower()
        if "ascended" in desc or any(token in inputs for token in ("gar", "gab", "gav", "gag", "gaw", "gpy", "gpr", "gpb", "gpg", "gpv", "gpw")) and "ascended" in desc:
            return "Ascended"
        if raw.get("input 2", "").strip().lower() in {"bct", "cct", "pct", "sct"}:
            return "Tablet"
        return "Classic"

    def _craft_family(self, raw: Dict[str, str], description: str) -> str:
        return self.analyzer._craft_family_name(raw.get("input 2", ""), description, raw)

    def _craft_variant_name(self, raw: Dict[str, str]) -> str:
        input_parts = self._token_parts(raw.get("input 1", ""))
        state_parts = [self.STATE_LABELS[part] for part in input_parts[1:] if part in self.STATE_LABELS and part != "nos"]
        ingredients = [raw.get(f"input {i}", "").strip().lower() for i in range(2, 8)]
        if "r05" in ingredients and "mls" in ingredients:
            state_parts.append("adds ethereal")
        return ", ".join(state_parts) if state_parts else "standard"

    def _craft_summary(self, source: str, family: str) -> str:
        source_text = {
            "Classic": "Classic jewel, rune, and perfect gem recipe.",
            "Tablet": "Tablet shortcut recipe using the matching crafting tablet.",
            "Ascended": "Ascended gem recipe with stronger endgame materials.",
        }.get(source, "Crafting recipe.")
        return f"{source_text} Shows fixed {family} properties by item type."

    def _ingredient_labels(self, raw: Dict[str, str], start: int = 1) -> List[str]:
        labels = []
        for index in range(start, 8):
            token = raw.get(f"input {index}", "").strip()
            if token and token != "0":
                labels.append(self.analyzer.resolve_token(token))
        return labels

    def _fixed_properties(self, raw: Dict[str, str]) -> List[str]:
        props = []
        for index in range(1, 6):
            code = raw.get(f"mod {index}", "").strip()
            if not code:
                continue
            resolved = self.analyzer.resolver.resolve_property(
                code,
                raw.get(f"mod {index} param", ""),
                raw.get(f"mod {index} min", ""),
                raw.get(f"mod {index} max", ""),
            )
            text = resolved.get("resolved_text", "").strip()
            if text and text not in props:
                props.append(text)
        return props

    def _is_pierce_recipe(self, recipe: CubeRecipeDTO) -> bool:
        desc = recipe.get("description", "").lower()
        haystack = " ".join([desc, " ".join(recipe.get("outputs", []))]).lower()
        return any(token in haystack for token in ("incendiary", "magnetic", "virulent", "gelid", "mystical", "breaching", "pierce-"))

    def _pierce_family(self, description: str) -> str:
        desc = description.lower()
        for family in ("Incendiary", "Magnetic", "Virulent", "Gelid", "Mystical", "Breaching"):
            if family.lower() in desc:
                return family
        return "Pierce"

    def _property_text(self, prop: str, raw: Dict[str, str]) -> str:
        if not prop:
            return ""
        resolved = self.analyzer.resolver.resolve_property(
            prop,
            raw.get("mod 1 param", ""),
            raw.get("mod 1 min", ""),
            raw.get("mod 1 max", ""),
        )
        return resolved.get("resolved_text", "") or prop

    def _token_base(self, token: str) -> str:
        parts = self._token_parts(token)
        return parts[0] if parts else ""

    @staticmethod
    def _token_parts(token: str) -> List[str]:
        return [part.strip().lower() for part in token.strip().strip('"').split(",") if part.strip()]

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
