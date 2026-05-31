from __future__ import annotations
import re
from typing import List, Dict, Optional, Any, Tuple
from d2lib.repository import D2Repository
from d2lib.models import CubeRecipeDTO, CubeRecipeGroupDTO
from d2lib.services.resolver import PropertyResolverService
from d2lib.services.base import _status_for_row, _slugify

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

    def __init__(self, repo: D2Repository, retail_repo: Optional[D2Repository] = None):
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
            if row.get('description')
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
        for i in range(1, 4):
            out = row.get('output' if i == 1 else f'output {i}', '').strip()
            if out and out != '0':
                mod_str = row.get(f'mod {i}', '').strip()
                mod_val = row.get(f'mod {i} param', '').strip()
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
        recipes_data = self.repo.get_excel_table('cubemain')
        all_recipes = [
            recipe
            for row in recipes_data
            if row.get('enabled') != '0'
            for recipe in [self.analyze_recipe(row)]
            if recipe["description"] or recipe["inputs"] or recipe["outputs"]
        ]

        if self.retail_repo:
            bk_recipe_keys = {
                row.get('description', '').strip().lower()
                for row in recipes_data
                if row.get('description') and row.get('enabled') != '0'
            }
            retail_analyzer = CubeAnalyzerService(self.retail_repo)
            for key, row in self.retail_recipe_rows.items():
                if key not in bk_recipe_keys and row.get('enabled') != '0':
                    all_recipes.append(retail_analyzer.analyze_recipe(row, status="removed"))

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
                "recipes": sorted(recipes, key=self._recipe_sort_key),
            }
            for name, recipes in sorted(
                groups.items(),
                key=lambda entry: (self.GROUP_META.get(entry[0], self.GROUP_META["General Recipes"])["order"], entry[0]),
            )
            for meta in [self.GROUP_META.get(name, self.GROUP_META["General Recipes"])]
        ]

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
                    "id": _slugify(" ".join(inputs)),
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
