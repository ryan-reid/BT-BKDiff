from __future__ import annotations

import os
import re
from typing import Any, Dict, List, Optional, Sequence, Tuple

from d2lib.models import PropertyDTO
from d2lib.repository import (
    D2RepositoryProtocol,
    get_charstats_class_rows,
    get_class_name_maps,
    resolve_localized_string,
)

_NUMBER_RE = re.compile(r"[+-]?\d+(?:\.\d+)?")
_PERCENT_FMT_RE = re.compile(r"%\+[diDI]")
_INT_FMT_RE = re.compile(r"%[diDI]")
_TIME_WRAPPER_KEYS: Dict[str, str] = {
    "0": "ModStre9e",  # Increases During Daytime
    "1": "ModStre9g",  # Increases Near Dusk
    "2": "ModStre9d",  # Increases During Nighttime
    "3": "ModStre9f",  # Increases Near Dawn
}
_MISSING_PROPERTY_GROUP_FALLBACKS: Dict[str, str] = {
    "gelid-affix5": "(Missing Affix 5 data)",
    "incendiary-affix5": "(Missing Affix 5 data)",
    "magnetic-affix5": "(Missing Affix 5 data)",
    "virulent-affix5": "(Missing Affix 5 data)",
    "breaching-affix5": "(Missing Affix 5 data)",
    "mystical-affix5": "(Missing Affix 5 data)",
}


def load_property_groups(
    repo: D2RepositoryProtocol,
    fallback_path: Optional[str] = None,
) -> List[Dict[str, str]]:
    """Loads propertygroups.txt from the repository first, falling back to repo-local data."""
    getter = getattr(repo, "get_excel_table", None)
    if callable(getter):
        rows = getter("propertygroups")
        if isinstance(rows, list) and rows:
            return rows
    loader = getattr(repo, "load_tsv", None)
    if callable(loader) and fallback_path:
        if os.path.exists(fallback_path) or not getattr(repo, "mpq_path", ""):
            rows = loader(fallback_path)
            if isinstance(rows, list) and rows:
                return rows
    return []


class PropertyResolverService:
    def __init__(self, repo: D2RepositoryProtocol, property_groups: Optional[List[Dict[str, str]]] = None):
        self.repo = repo
        effective_groups = property_groups if property_groups is not None else load_property_groups(repo)
        self.property_groups: Dict[str, Dict[str, str]] = {
            row["code"].strip().lower(): row
            for row in effective_groups
            if row.get("code", "").strip()
        }

        self.properties: Dict[str, Dict[str, str]] = {
            row.get("code", "").strip().lower(): row
            for row in repo.get_excel_table("properties")
            if row.get("code", "").strip()
        }
        self.stats: Dict[str, Dict[str, str]] = {
            row.get("Stat", "").strip().lower(): row
            for row in repo.get_excel_table("itemstatcost")
            if row.get("Stat", "").strip()
        }

        skills_data = repo.get_excel_table("skills")
        self.skills: Dict[str, Dict[str, str]] = {
            row.get("skill", "").strip().lower(): row
            for row in skills_data
            if row.get("skill", "").strip()
        }
        self.skills_by_id: Dict[str, Dict[str, str]] = {}
        for row in skills_data:
            s_id = row.get("*Id") or row.get("Id") or row.get("*ID") or row.get("ID")
            if s_id:
                self.skills_by_id[str(s_id).strip()] = row

        self.skill_desc: Dict[str, Dict[str, str]] = {
            row.get("skilldesc", "").strip().lower(): row
            for row in repo.get_excel_table("skilldesc")
            if row.get("skilldesc", "").strip()
        }
        class_rows = get_charstats_class_rows(repo)
        self.class_names, self.class_abbr_map = get_class_name_maps(repo)
        self.class_only_qualifiers: Dict[str, str] = {}

        self.skill_to_class: Dict[str, str] = {}
        for row in skills_data:
            s_name = row.get("skill", "").strip().lower()
            s_id = row.get("*Id") or row.get("Id") or row.get("*ID") or row.get("ID")
            charclass = row.get("charclass", "").strip().lower()
            if charclass:
                if s_name:
                    self.skill_to_class[s_name] = charclass
                if s_id:
                    self.skill_to_class[str(s_id).strip()] = charclass

        self.class_skill_templates: Dict[str, str] = {}
        self.skill_tab_templates: Dict[str, str] = {}
        self.skill_tab_classes: Dict[str, str] = {}
        for class_index, row in enumerate(class_rows):
            raw_class = row.get("class", "").strip()
            key = row.get("StrAllSkills", "")
            text = resolve_localized_string(repo, key)
            if key and text:
                self.class_skill_templates[str(class_index)] = text
            class_key = row.get("StrClassOnly", "")
            qualifier = resolve_localized_string(repo, class_key)
            if not qualifier:
                localized_class = resolve_localized_string(repo, raw_class) or raw_class
                qualifier = f"({localized_class})" if localized_class else ""
            if raw_class:
                self.class_only_qualifiers[raw_class[:3].casefold()] = qualifier
            for tab in range(3):
                key = row.get(f"StrSkillTab{tab + 1}", "")
                text = resolve_localized_string(repo, key)
                tab_id = str(class_index * 3 + tab)
                if key and text:
                    self.skill_tab_templates[tab_id] = text
                    self.skill_tab_classes[tab_id] = qualifier

        self.monsters_by_hcidx: Dict[str, str] = {}
        self.monsters_by_id: Dict[str, str] = {}
        for row in repo.get_excel_table("monstats"):
            namestr = str(row.get("NameStr", "")).strip()
            localized = resolve_localized_string(repo, namestr) or namestr
            if not localized:
                continue
            hcidx = str(row.get("*hcIdx", "")).strip()
            mon_id = str(row.get("Id", "")).strip().casefold()
            if hcidx and hcidx not in self.monsters_by_hcidx:
                self.monsters_by_hcidx[hcidx] = localized
            if mon_id and mon_id not in self.monsters_by_id:
                self.monsters_by_id[mon_id] = localized

        self.montypes: Dict[str, str] = {}
        for row in repo.get_excel_table("montype"):
            mtype = str(row.get("type", "")).strip().casefold()
            if not mtype:
                continue
            name_key = str(row.get("strplur") or row.get("strsing") or "").strip()
            localized = resolve_localized_string(repo, name_key) or name_key
            if localized:
                self.montypes[mtype] = localized

        # Legacy empty attribute left for backwards compatibility with callers/tests.
        self.manual_overrides: Dict[str, str] = {}

    def _loc(self, key: str) -> str:
        return resolve_localized_string(self.repo, key)

    @staticmethod
    def _format_decimal(value: float) -> str:
        text = f"{value:.3f}".rstrip("0").rstrip(".")
        return text or "0"

    @staticmethod
    def _range_text(min_val: str, max_val: str) -> str:
        if not min_val and not max_val:
            return ""
        if min_val == max_val or not max_val:
            return min_val
        if not min_val:
            return max_val
        return f"{min_val}-{max_val}"

    @staticmethod
    def _parse_int(raw: str, default: int = 0) -> int:
        try:
            return int(str(raw).strip())
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _parse_numeric_values(*raw_values: str) -> List[float]:
        values: List[float] = []
        for raw in raw_values:
            text = str(raw or "").strip()
            if not text:
                continue
            try:
                values.append(float(text))
            except ValueError:
                values.extend(float(match) for match in _NUMBER_RE.findall(text))
        return values

    @staticmethod
    def _substitute_numeric(fmt_string: str, range_str: str, v_min: int) -> str:
        text = fmt_string
        sign = "+" if v_min >= 0 else ""
        if _PERCENT_FMT_RE.search(text):
            replacement = range_str if range_str.startswith(("+", "-")) else f"{sign}{range_str}"
            text = _PERCENT_FMT_RE.sub(lambda _: replacement, text)
        elif _INT_FMT_RE.search(text):
            if "-%d" in text.lower() and range_str.startswith("-"):
                text = re.sub(r"-%[diDI]", lambda _: range_str, text)
            else:
                text = _INT_FMT_RE.sub(lambda _: range_str, text)
        return text.replace("%%", "%")

    @staticmethod
    def label_from_template(template: str, protected_names: Sequence[str] = ()) -> str:
        """Extracts an unvalued localized stat label from a format template or resolved string."""
        text = str(template or "").strip()
        if not text:
            return ""
        replacements: Dict[str, str] = {}
        for index, name in enumerate(protected_names):
            clean = str(name or "").strip()
            if clean and clean in text:
                marker = f"__d2p{index}__"
                text = text.replace(clean, marker)
                replacements[marker] = clean

        placeholder_or_num = (
            r"(?:[+\-]?\s*%\+?[diDI](?:%%|%)?"
            r"|[+\-]?\s*%\d+(?:%%|%)?"
            r"|[+\-]?#(?:\s*-\s*#)?%?"
            r"|[+\-]?\d+(?:\.\d+)?(?:-[+\-]?\d+(?:\.\d+)?)?%?)"
        )
        had_leading_placeholder = bool(
            re.match(rf"^(?:\(?{placeholder_or_num}\)?|Adds\s+{placeholder_or_num})", text, re.IGNORECASE)
        )
        text = re.sub(r"\([^)]*%\+?[diDI][^)]*\)", lambda m: m.group(0) if "/" in m.group(0) else "", text)
        text = re.sub(r"[+\-]?\s*%\+?[diDI](?:%%|%)?", "", text)
        text = re.sub(r"[+\-]?\s*%\d+(?:%%|%)?", "", text)
        text = text.replace("%s", "")
        text = re.sub(r"[+\-]?#(?:\s*-\s*#)?%?", "", text)
        text = re.sub(r"(?<![A-Za-z0-9_])[+\-]?\d+(?:\.\d+)?(?:-[+\-]?\d+(?:\.\d+)?)?%?", "", text)
        text = text.replace("%%", "%")
        text = re.sub(r"\(\s*[/:\-\s]*\s*\)", "", text)
        text = re.sub(r"\(\s*[/:\-\s]+", "(", text)
        text = re.sub(r"\s+", " ", text).strip(" +-:/·")
        text = text.lstrip("% ").strip()
        if had_leading_placeholder:
            text = re.sub(r"^(?:to|zu)\s+", "", text, flags=re.IGNORECASE)
        else:
            text = re.sub(r"^(?:Adds)\s+", "", text)
        text = re.sub(r"\s+", " ", text).strip(" +-:/·")

        for marker, name in replacements.items():
            text = text.replace(marker, name)
        return text[0].upper() + text[1:] if text else ""

    @staticmethod
    def _make_dto(
        code: str,
        param: str,
        min_val: str,
        max_val: str,
        resolved_text: str,
        *,
        canonical_code: str = "",
        stats: Optional[List[str]] = None,
        label: str = "",
        numeric_values: Optional[List[float]] = None,
        parameter_key: str = "",
        base_text: str = "",
        is_unknown: bool = False,
    ) -> PropertyDTO:
        dto: PropertyDTO = {
            "code": code,
            "param": param,
            "min_val": min_val,
            "max_val": max_val,
            "resolved_text": resolved_text,
            "canonical_code": canonical_code or code.strip().lower(),
            "stats": list(stats or []),
            "label": label,
            "numeric_values": list(numeric_values or []),
            "parameter_key": parameter_key,
            "is_unknown": is_unknown,
        }
        if base_text:
            dto["base_text"] = base_text
        return dto

    def _resolve_skill_row(self, skill_name_or_id: str) -> Optional[Dict[str, str]]:
        clean = str(skill_name_or_id).strip()
        if not clean or clean == "0":
            return None
        return self.skills_by_id.get(clean) if clean.isdigit() else self.skills.get(clean.lower())

    def resolve_skill_name(self, skill_name_or_id: str) -> str:
        clean = str(skill_name_or_id).strip()
        if not clean or clean == "0":
            return clean
        skill = self._resolve_skill_row(clean)
        if skill:
            desc_key = skill.get("skilldesc", "").strip().lower()
            if desc_key in self.skill_desc:
                str_name_key = self.skill_desc[desc_key].get("str name", "").strip()
                resolved = self.repo.get_string(str_name_key)
                if resolved:
                    return resolved
            return skill.get("skill", "").strip()
        return clean

    def _skill_qualifier(self, skill_name_or_id: str) -> str:
        skill = self._resolve_skill_row(skill_name_or_id)
        if not skill:
            return ""
        cc = skill.get("charclass", "").strip().casefold()
        return self.class_only_qualifiers.get(cc, "")

    def _stat_meta(self, prop: Dict[str, str]) -> List[str]:
        return [
            prop.get(f"stat{i}", "").strip()
            for i in range(1, 8)
            if prop.get(f"stat{i}", "").strip()
        ]

    def _format_stat_entry(
        self,
        stat: Dict[str, str],
        min_val: str,
        max_val: str,
        param: str = "",
        *,
        use_dgrp: bool = False,
    ) -> Optional[Tuple[str, str, List[float], str]]:
        prefix = "dgrp" if use_dgrp else "desc"
        str_pos = stat.get(f"{prefix}strpos", "").strip()
        str_neg = stat.get(f"{prefix}strneg", "").strip()
        str_2 = stat.get(f"{prefix}str2", "").strip()
        if not str_pos:
            return None

        v_min = self._parse_int(min_val, 0)
        v_max = self._parse_int(max_val, v_min)
        desc_func = stat.get(f"{prefix}func", "0").strip()
        desc_val = stat.get(f"{prefix}val", "").strip()
        op_base = stat.get("op base", "").strip().lower()
        range_str = self._range_text(min_val, max_val)

        str_key = str_pos if (v_min >= 0 or not str_neg) else str_neg
        fmt_string = self._loc(str_key)
        if not fmt_string:
            return None
        str_2_text = self._loc(str_2) if str_2 else ""

        # 1. Per-character-level stats (op base = level)
        if not use_dgrp and op_base == "level":
            op_param = self._parse_int(stat.get("op param", "0"), 0)
            factor = 2 ** op_param
            p_min = v_min / factor
            p_max = v_max / factor
            p_range = (
                self._format_decimal(p_min)
                if p_min == p_max
                else f"{self._format_decimal(p_min)}-{self._format_decimal(p_max)}"
            )
            num_vals = [p_min] if p_min == p_max else [p_min, p_max]
            text = self._substitute_numeric(fmt_string, p_range, 1 if p_min >= 0 else -1)
            label = self.label_from_template(fmt_string)
            if str_2_text:
                text = f"{text} {str_2_text}".strip()
                label = f"{label} {str_2_text}".strip()
            return text, label, num_vals, ""

        # 2. Time-of-day stats (descfunc 17, 18)
        if desc_func in {"17", "18"}:
            base_text = self._substitute_numeric(fmt_string, range_str, v_min)
            wrapper_key = _TIME_WRAPPER_KEYS.get(str(param).strip(), "ModStre9d")
            wrapper = self._loc(wrapper_key)
            if wrapper and "%s" in wrapper:
                text = wrapper.replace("%s", base_text)
                label_wrapper = wrapper.replace("%s", self.label_from_template(fmt_string))
                return text, label_wrapper, self._parse_numeric_values(min_val, max_val), str(param).strip()
            return (
                f"{base_text} {str_2_text}".strip() if str_2_text else base_text,
                self.label_from_template(fmt_string),
                self._parse_numeric_values(min_val, max_val),
                str(param).strip(),
            )

        # 3. Howl / monster flee percentage (descfunc 5): 128 == 100%
        if desc_func == "5":
            scaled_min = round(v_min * 100 / 128)
            scaled_max = round(v_max * 100 / 128)
            scaled_range = str(scaled_min) if scaled_min == scaled_max else f"{scaled_min}-{scaled_max}"
            text = self._substitute_numeric(fmt_string, scaled_range, scaled_min)
            return text, self.label_from_template(fmt_string), [float(scaled_min)] if scaled_min == scaled_max else [float(scaled_min), float(scaled_max)], ""

        # 4. Replenish durability (descfunc 11)
        if desc_func == "11":
            val = self._parse_int(min_val or param, 0)
            if val >= 100:
                per_sec = val // 100
                text = self._substitute_numeric(fmt_string, str(per_sec), per_sec)
                return text, self.label_from_template(fmt_string), [float(per_sec)], ""
            if val > 0:
                seconds = max(1, round(100 / val))
                in_sec_fmt = self._loc("ModStre9u")
                if in_sec_fmt and in_sec_fmt.count("%d") >= 2:
                    text = in_sec_fmt.replace("%d", "1", 1).replace("%d", str(seconds), 1)
                    return text, self.label_from_template(in_sec_fmt), [1.0, float(seconds)], ""
                text = self._substitute_numeric(fmt_string, str(val), val)
                return text, self.label_from_template(fmt_string), [float(val)], ""

        # 5. Chance to cast on attack/striking/struck/kill/death/level-up (descfunc 15)
        if desc_func == "15":
            if "%" not in fmt_string:
                return fmt_string, self.label_from_template(fmt_string), self._parse_numeric_values(min_val, max_val), ""
            skill_name = self.resolve_skill_name(param)
            chance = min_val or "0"
            level = max_val or min_val or "1"
            text = fmt_string.replace("%%", "%")
            text = _INT_FMT_RE.sub(lambda _: chance, text, count=1)
            text = _INT_FMT_RE.sub(lambda _: level, text, count=1)
            text = text.replace("%s", skill_name)
            label = self.label_from_template(text, protected_names=[skill_name])
            return text, label, self._parse_numeric_values(chance, level), str(param).strip()

        # 6. Aura when equipped (descfunc 16)
        if desc_func == "16":
            skill_name = self.resolve_skill_name(param)
            text = self._substitute_numeric(fmt_string, range_str, v_min).replace("%s", skill_name)
            label = self.label_from_template(text, protected_names=[skill_name])
            return text, label, self._parse_numeric_values(min_val, max_val), str(param).strip()

        # 7. Attack Rating / Damage vs Monster Type (descfunc 22)
        if desc_func == "22":
            mon_type = self.montypes.get(str(param).strip().casefold()) or self._loc(str(param).strip()) or str(param).strip()
            base_text = self._substitute_numeric(fmt_string, range_str, v_min)
            text = f"{base_text} {mon_type}".strip()
            label = self.label_from_template(text, protected_names=[mon_type] if mon_type else ())
            return text, label, self._parse_numeric_values(min_val, max_val), str(param).strip()

        # 8. Reanimate as: monster (descfunc 23)
        if desc_func == "23":
            mon_key = str(param).strip()
            mon_name = (
                self.monsters_by_hcidx.get(mon_key)
                or self.monsters_by_id.get(mon_key.casefold())
                or self._loc(mon_key)
                or mon_key
            )
            low_pct, high_pct = sorted((v_min, v_max))
            pct_str = str(low_pct) if low_pct == high_pct else f"{low_pct}-{high_pct}"
            text = fmt_string.replace("%%", "%").replace("%0", pct_str).replace("%1", mon_name)
            label = self.label_from_template(text, protected_names=[mon_name] if mon_name else ())
            nums = [float(low_pct)] if low_pct == high_pct else [float(low_pct), float(high_pct)]
            return text, label, nums, mon_key

        # 9. Charged skill (descfunc 24)
        if desc_func == "24":
            skill_name = self.resolve_skill_name(param)
            charges = min_val or "0"
            level = max_val or min_val or "1"
            text = fmt_string.replace("%%", "%")
            text = _INT_FMT_RE.sub(lambda _: level, text, count=1)
            text = text.replace("%s", skill_name, 1)
            text = _INT_FMT_RE.sub(lambda _: charges, text, count=1)
            text = _INT_FMT_RE.sub(lambda _: charges, text, count=1)
            label = self.label_from_template(text, protected_names=[skill_name])
            return text, label, self._parse_numeric_values(level, charges), str(param).strip()

        # 10. Single class skill + class-only qualifier (descfunc 27)
        if desc_func == "27":
            skill_name = self.resolve_skill_name(param)
            qualifier = self._skill_qualifier(param)
            text = self._substitute_numeric(fmt_string, range_str, v_min)
            text = text.replace("%s", skill_name, 1).replace("%s", qualifier, 1)
            text = re.sub(r"\s+", " ", text).strip()
            label = self.label_from_template(text, protected_names=[skill_name, qualifier])
            return text, label, self._parse_numeric_values(min_val, max_val), str(param).strip()

        # 11. Oskill (descfunc 28)
        if desc_func == "28":
            skill_name = self.resolve_skill_name(param)
            text = self._substitute_numeric(fmt_string, range_str, v_min).replace("%s", skill_name)
            label = self.label_from_template(text, protected_names=[skill_name])
            return text, label, self._parse_numeric_values(min_val, max_val), str(param).strip()

        # 12. Freeze Target / Blinds Target (descfunc 12)
        if desc_func == "12":
            text = fmt_string.replace("%%", "%")
            if min_val != max_val or abs(v_min) > 1:
                signed = range_str if range_str.startswith(("+", "-")) else f"+{range_str}"
                if desc_val == "1":
                    text = f"{signed} {text}"
                elif desc_val == "2":
                    text = f"{text} {signed}"
            if str_2_text:
                text = f"{text} {str_2_text}".strip()
            return text, self.label_from_template(fmt_string), self._parse_numeric_values(min_val, max_val), ""

        # 13. Format strings with placeholders (descfunc 19, 29, or any template with %d/%i)
        if _PERCENT_FMT_RE.search(fmt_string) or _INT_FMT_RE.search(fmt_string):
            text = self._substitute_numeric(fmt_string, range_str, v_min)
            if str_2_text:
                text = f"{text} {str_2_text}".strip()
            label = self.label_from_template(fmt_string)
            if str_2_text:
                label = f"{label} {str_2_text}".strip()
            return text, label, self._parse_numeric_values(min_val, max_val), ""

        # 14. Classic descval formatting without inline %d placeholders (descfunc 1..9, 20, etc.)
        text = fmt_string.replace("%%", "%")
        if desc_val != "0" and range_str:
            is_pct = desc_func in {"2", "4", "7", "8", "20"}
            needs_sign = desc_func in {"1", "4", "6", "7", "8"}
            prefix_sign = "+" if (needs_sign and v_min >= 0 and not range_str.startswith(("+", "-"))) else ""
            suffix_pct = "%" if is_pct else ""
            formatted_val = f"{prefix_sign}{range_str}{suffix_pct}"
            if desc_val == "1":
                text = f"{formatted_val} {text}"
            elif desc_val == "2":
                sep = "" if text.endswith((" ", ":")) else " "
                text = f"{text}{sep}{formatted_val}"
            elif desc_func == "3" and desc_val == "" and text.endswith("x"):
                text = f"{text}{range_str}"
        if str_2_text:
            text = f"{text} {str_2_text}".strip()
        label = self.label_from_template(fmt_string)
        if str_2_text:
            label = f"{label} {str_2_text}".strip()
        return text, label, self._parse_numeric_values(min_val, max_val), ""

    def format_desc(self, stat_code: str, min_val: str, max_val: str, param: str = "") -> Optional[str]:
        stat = self.stats.get(stat_code.lower())
        if not stat:
            return None
        formatted = self._format_stat_entry(stat, min_val, max_val, param, use_dgrp=False)
        return formatted[0] if formatted else None

    def _resolve_tooltip_fallback(
        self,
        code_orig: str,
        code_lower: str,
        prop: Dict[str, str],
        param: str,
        min_val: str,
        max_val: str,
        actual_min: str,
        actual_max: str,
        range_str: str,
    ) -> Optional[PropertyDTO]:
        tooltip = prop.get("*Tooltip", "").strip()
        if not tooltip or tooltip == "0":
            return None
        func, val1 = prop.get("func1", "0").strip(), prop.get("val1", "0").strip()
        res_text = tooltip
        display_range = range_str
        if "-#" in res_text:
            try:
                display_min = str(abs(int(actual_min))) if actual_min else actual_min
                display_max = str(abs(int(actual_max))) if actual_max else actual_max
                display_range = display_min if display_min == display_max else f"{display_min}-{display_max}"
            except ValueError:
                display_range = range_str
        if func == "36":
            res_text = res_text.replace("#", val1)
        elif res_text.count("#") > 1 and "-" in display_range:
            for part in display_range.split("-"):
                res_text = res_text.replace("#", part, 1)
        else:
            res_text = res_text.replace("#", display_range)

        if code_lower == "pierce" and "#" not in tooltip and display_range:
            res_text = f"{display_range}% {res_text}"

        protected: List[str] = []
        param_key = ""
        if "[Class Skill Tab]" in res_text:
            tab_label = f"Tab {param}"
            res_text = res_text.replace("[Class Skill Tab]", tab_label)
            protected.append(tab_label)
            param_key = str(param).strip()
        if "[Class]" in res_text:
            if func == "36":
                cls = "Random Class" if actual_min != actual_max else self.class_names.get(actual_min, f"Class {actual_min}")
            else:
                set1 = prop.get("set1", "").strip()
                cls_id = set1 if set1 and set1 != "0" else param
                cls = self.class_names.get(str(cls_id))
                if not cls:
                    skill_cls_abbr = self.skill_to_class.get(str(param).strip().lower())
                    if skill_cls_abbr:
                        cls = self.class_abbr_map.get(skill_cls_abbr)
                if not cls:
                    cls = "Class"
            res_text = res_text.replace("[Class]", cls)
            protected.append(cls)
        if "[Skill]" in res_text or "%s" in res_text:
            skill_name = self.resolve_skill_name(param)
            res_text = res_text.replace("[Skill]", skill_name).replace("%s", skill_name)
            protected.append(skill_name)
            param_key = str(param).strip()

        label = self.label_from_template(tooltip.replace("[Class Skill Tab]", f"Tab {param}").replace("[Skill]", self.resolve_skill_name(param) if "[Skill]" in tooltip else "").replace("%s", self.resolve_skill_name(param) if "%s" in tooltip else ""), protected_names=protected)
        if "[Skill]" in tooltip or "%s" in tooltip or "[Class Skill Tab]" in tooltip or "[Class]" in tooltip:
            label = self.label_from_template(res_text, protected_names=protected)
        return self._make_dto(
            code_orig,
            param,
            min_val,
            max_val,
            res_text,
            canonical_code=code_lower,
            stats=self._stat_meta(prop) or [code_lower],
            label=label,
            numeric_values=self._parse_numeric_values(actual_min, actual_max, param if func == "14" else ""),
            parameter_key=param_key,
        )

    def _resolve_engine_native(
        self,
        code_orig: str,
        code_lower: str,
        prop: Dict[str, str],
        param: str,
        min_val: str,
        max_val: str,
        actual_min: str,
        actual_max: str,
        range_str: str,
    ) -> Optional[PropertyDTO]:
        func1 = prop.get("func1", "0").strip()
        stats = self._stat_meta(prop)
        num_vals = self._parse_numeric_values(actual_min, actual_max)
        v_min = self._parse_int(actual_min, 0)

        # Skill tabs and class skills (already driven by charstats localization)
        if code_lower == "skilltab":
            template = self.skill_tab_templates.get(str(param))
            if template:
                text = self._substitute_numeric(template, range_str, v_min)
                return self._make_dto(
                    code_orig, param, min_val, max_val, text,
                    canonical_code=code_lower, stats=stats or ["item_addskill_tab"],
                    label=self.label_from_template(template),
                    numeric_values=num_vals, parameter_key=str(param).strip(),
                )
        elif code_lower == "war-tab-rand" or (prop.get("stat1") == "item_addskill_tab" and func1 == "10" and len(stats) > 1):
            options = [
                self._substitute_numeric(self.skill_tab_templates[prop[f"val{i}"]], range_str, v_min)
                for i in range(1, 8)
                if prop.get(f"val{i}") in self.skill_tab_templates
            ]
            if options:
                text = self._format_group_options(options, pick_mode="2")
                return self._make_dto(
                    code_orig, param, min_val, max_val, text,
                    canonical_code=code_lower, stats=stats,
                    label=self.label_from_template(text), numeric_values=num_vals,
                )
        elif prop.get("stat1") == "item_addclassskills" and func1 == "21":
            template = self.class_skill_templates.get(prop.get("val1", ""))
            if template:
                text = self._substitute_numeric(template, range_str, v_min)
                return self._make_dto(
                    code_orig, param, min_val, max_val, text,
                    canonical_code=code_lower, stats=stats,
                    label=self.label_from_template(template), numeric_values=num_vals,
                    parameter_key=prop.get("val1", "").strip(),
                )
        elif prop.get("stat1") == "item_addclassskills" and func1 == "36":
            val1 = prop.get("val1", "").strip() or "1"
            v1_int = self._parse_int(val1, 1)
            if actual_min == actual_max and actual_min in self.class_skill_templates:
                template = self.class_skill_templates[actual_min]
                text = self._substitute_numeric(template, val1, v1_int)
                return self._make_dto(
                    code_orig, param, min_val, max_val, text,
                    canonical_code=code_lower, stats=stats,
                    label=self.label_from_template(template), numeric_values=[float(v1_int)],
                    parameter_key=actual_min,
                )
            rand_tpl = self._loc("chronicleRandomClassSkillLevel")
            if rand_tpl:
                text = self._substitute_numeric(rand_tpl, val1, v1_int)
                return self._make_dto(
                    code_orig, param, min_val, max_val, text,
                    canonical_code=code_lower, stats=stats,
                    label=self.label_from_template(rand_tpl), numeric_values=[float(v1_int)],
                )

        # Random skill from a class range (func1 = 12, e.g. Ormus' Robes)
        if func1 == "12" or code_lower == "skill-rand":
            bonus = param.strip() if str(param).strip() else "1"
            b_int = self._parse_int(bonus, 1)
            sk_row = self.skills_by_id.get(actual_min, {})
            c_abbr = sk_row.get("charclass", "").strip().lower()
            cls_name = self.class_abbr_map.get(c_abbr, "")
            qualifier = self.class_only_qualifiers.get(c_abbr, "")
            tpl = self._loc("chronicleItemModifierClassSkillRandom")
            if tpl and cls_name:
                text = self._substitute_numeric(tpl, bonus, b_int)
                text = text.replace("%s", cls_name, 1).replace("%s", qualifier, 1)
                text = re.sub(r"\s+", " ", text).strip()
                label = self.label_from_template(text, protected_names=[cls_name, qualifier])
                return self._make_dto(
                    code_orig, param, min_val, max_val, text,
                    canonical_code=code_lower, stats=stats or ["item_singleskill"],
                    label=label, numeric_values=[float(b_int)],
                    parameter_key=f"{actual_min}-{actual_max}",
                )
            if not prop.get("*Tooltip"):
                fallback_cls = cls_name or "Class"
                text = f"+{bonus} to Random {fallback_cls} Skill"
                return self._make_dto(
                    code_orig, param, min_val, max_val, text,
                    canonical_code=code_lower, stats=stats or ["item_singleskill"],
                    label=f"Random {fallback_cls} Skill", numeric_values=[float(b_int)],
                    parameter_key=f"{actual_min}-{actual_max}",
                )

        # Cold / Poison duration properties
        if code_lower == "cold-len":
            return self._resolve_cold_length(code_orig, param, min_val, max_val, actual_min, actual_max, stats)
        if code_lower == "pois-len":
            dur_text = self._format_frame_duration(actual_min, actual_max)
            text = f"Poison Duration: {dur_text}"
            return self._make_dto(
                code_orig, param, min_val, max_val, text,
                canonical_code=code_lower, stats=stats or ["poisonlength"],
                label="Poison Duration", numeric_values=self._parse_numeric_values(actual_min, actual_max),
            )

        # Elemental range helpers
        def elemental_range(range_key: str, single_key: str, default_label: str) -> Optional[Tuple[str, str]]:
            if actual_min == actual_max and single_key:
                single_tpl = self._loc(single_key)
                if single_tpl:
                    return self._substitute_numeric(single_tpl, actual_min, v_min), self.label_from_template(single_tpl)
            range_tpl = self._loc(range_key)
            if range_tpl:
                text = range_tpl.replace("%d", actual_min, 1).replace("%d", actual_max, 1) if actual_min != actual_max else (
                    self._loc(single_key) and self._substitute_numeric(self._loc(single_key), actual_min, v_min)
                    or range_tpl.replace("%d-%d", actual_min).replace("%d - %d", actual_min).replace("%d", actual_min, 1)
                )
                return text, self.label_from_template(self._loc(single_key) or range_tpl)
            return None

        if code_lower == "dmg-norm":
            formatted = elemental_range("strModMinDamageRange", "strModMinDamage", "Damage")
            if formatted:
                return self._make_dto(
                    code_orig, param, min_val, max_val, formatted[0],
                    canonical_code=code_lower, stats=stats, label=formatted[1], numeric_values=num_vals,
                )
        if code_lower == "dmg-fire":
            formatted = elemental_range("strModFireDamageRange", "strModFireDamage", "Fire Damage")
            if formatted:
                return self._make_dto(
                    code_orig, param, min_val, max_val, formatted[0],
                    canonical_code=code_lower, stats=stats, label=formatted[1], numeric_values=num_vals,
                )
        if code_lower == "dmg-ltng":
            formatted = elemental_range("strModLightningDamageRange", "strModLightningDamage", "Lightning Damage")
            if formatted:
                return self._make_dto(
                    code_orig, param, min_val, max_val, formatted[0],
                    canonical_code=code_lower, stats=stats, label=formatted[1], numeric_values=num_vals,
                )
        if code_lower == "dmg-mag":
            formatted = elemental_range("strModMagicDamageRange", "strModMagicDamage", "Magic Damage")
            if formatted:
                return self._make_dto(
                    code_orig, param, min_val, max_val, formatted[0],
                    canonical_code=code_lower, stats=stats, label=formatted[1], numeric_values=num_vals,
                )
        if code_lower == "dmg-cold":
            formatted = elemental_range("strModColdDamageRange", "strModColdDamage", "Cold Damage")
            if formatted:
                base_text, label = formatted
            elif not prop.get("*Tooltip"):
                base_text, label = f"Adds {actual_min}-{actual_max} Cold Damage", "Cold Damage"
            else:
                return None
            duration = self.cold_duration(code_lower, param, actual_min, actual_max)
            text = base_text
            if duration:
                len_dto = self._resolve_cold_length("cold-len", "", str(duration[0]), str(duration[1]), str(duration[0]), str(duration[1]), ["coldlength"])
                text += f" · {len_dto['resolved_text']}"
            return self._make_dto(
                code_orig, param, min_val, max_val, text,
                canonical_code=code_lower, stats=stats or ["coldmindam", "coldmaxdam", "coldlength"],
                label=label, numeric_values=num_vals, base_text=base_text,
            )

        if code_lower == "dmg-pois":
            frames = self._parse_int(param, 0)
            if frames > 0:
                seconds = frames / 25
                sec_str = self._format_decimal(seconds)
                if actual_min == actual_max:
                    tpl = self._loc("strModPoisonDamage")
                    if tpl:
                        signed = actual_min if actual_min.startswith(("+", "-")) else f"+{actual_min}"
                        text = _PERCENT_FMT_RE.sub(lambda _: signed, tpl, count=1)
                        text = _INT_FMT_RE.sub(lambda _: sec_str, text, count=1)
                        label = self.label_from_template(self._loc("strskill8") or "Poison Damage")
                        return self._make_dto(
                            code_orig, param, min_val, max_val, text,
                            canonical_code=code_lower, stats=stats or ["poisonmindam", "poisonmaxdam", "poisonlength"],
                            label=label, numeric_values=num_vals,
                        )
                else:
                    tpl = self._loc("strModPoisonDamageRange")
                    if tpl:
                        text = (
                            tpl.replace("%d", actual_min, 1)
                            .replace("%d", actual_max, 1)
                            .replace("%d", sec_str, 1)
                        )
                        label = self.label_from_template(self._loc("strskill8") or "Poison Damage")
                        return self._make_dto(
                            code_orig, param, min_val, max_val, text,
                            canonical_code=code_lower, stats=stats or ["poisonmindam", "poisonmaxdam", "poisonlength"],
                            label=label, numeric_values=num_vals,
                        )
                text = f"Adds {range_str} Poison Damage Over {sec_str} Seconds"
                return self._make_dto(
                    code_orig, param, min_val, max_val, text,
                    canonical_code=code_lower, stats=stats or ["poisonmindam", "poisonmaxdam", "poisonlength"],
                    label="Poison Damage", numeric_values=num_vals,
                )
            else:
                tpl = self._loc("strskill8")
                if tpl:
                    if actual_min == actual_max:
                        text = re.sub(r"%d\s*-\s*%d", lambda _: actual_min, tpl)
                    else:
                        text = tpl.replace("%d", actual_min, 1).replace("%d", actual_max, 1)
                    return self._make_dto(
                        code_orig, param, min_val, max_val, text,
                        canonical_code=code_lower, stats=stats or ["poisonmindam", "poisonmaxdam", "poisonlength"],
                        label=self.label_from_template(tpl), numeric_values=num_vals,
                    )
                return self._make_dto(
                    code_orig, param, min_val, max_val, f"Adds {range_str} Poison Damage",
                    canonical_code=code_lower, stats=stats or ["poisonmindam", "poisonmaxdam", "poisonlength"],
                    label="Poison Damage", numeric_values=num_vals,
                )

        if code_lower == "dmg-elem":
            parts = []
            for key in ("strModFireDamageRange", "strModLightningDamageRange", "strModColdDamageRange"):
                tpl = self._loc(key)
                if tpl:
                    parts.append(tpl.replace("%d", actual_min, 1).replace("%d", actual_max, 1))
            if parts:
                text = " / ".join(parts)
                return self._make_dto(
                    code_orig, param, min_val, max_val, text,
                    canonical_code=code_lower, stats=stats,
                    label=" / ".join(self.label_from_template(self._loc(k)) for k in ("strModFireDamage", "strModLightningDamage", "strModColdDamage") if self._loc(k)) or "Elemental Damage",
                    numeric_values=num_vals,
                )

        if code_lower == "dmg-throw":
            tpl = self._loc("strItemStatThrowDamageRange")
            if tpl and actual_min != actual_max:
                text = tpl.replace("%d", actual_min, 1).replace("%d", actual_max, 1)
                return self._make_dto(
                    code_orig, param, min_val, max_val, text,
                    canonical_code=code_lower, stats=stats, label=self.label_from_template(tpl), numeric_values=num_vals,
                )
            single_tpl = self._loc("ItemStats1n")
            if single_tpl:
                text = self._substitute_numeric(single_tpl, range_str, v_min)
                return self._make_dto(
                    code_orig, param, min_val, max_val, text,
                    canonical_code=code_lower, stats=stats, label=self.label_from_template(single_tpl), numeric_values=num_vals,
                )

        # Engine-native properties lacking itemstatcost descstrpos
        key_only_specs: Dict[str, Tuple[str, Optional[List[str]]]] = {
            "dmg-min": ("ModStr1g", ["mindamage"]),
            "dmg-max": ("ModStr1f", ["maxdamage"]),
            "dmg%": ("strModEnhancedDamage", ["item_mindamage_percent", "item_maxdamage_percent"]),
            "levelreq": ("ItemStats1p", ["item_levelreq"]),
        }
        if code_lower in key_only_specs:
            str_key, default_stats = key_only_specs[code_lower]
            tpl = self._loc(str_key)
            if tpl:
                text = self._substitute_numeric(tpl, range_str, v_min)
                return self._make_dto(
                    code_orig, param, min_val, max_val, text,
                    canonical_code=code_lower, stats=stats or list(default_stats or []),
                    label=self.label_from_template(tpl), numeric_values=num_vals,
                )

        if code_lower == "dur" or prop.get("stat1") == "maxdurability":
            tpl = self._loc("ItemStats1d")
            if tpl:
                max_part = actual_max or actual_min
                text = tpl.replace("%i", actual_min, 1).replace("%i", max_part, 1)
                return self._make_dto(
                    code_orig, param, min_val, max_val, text,
                    canonical_code=code_lower, stats=stats or ["maxdurability"],
                    label=self.label_from_template(tpl), numeric_values=num_vals,
                )

        if code_lower == "sock" or func1 == "14":
            tpl = self._loc("Socketable")
            if tpl:
                text = self._substitute_numeric(tpl, range_str, v_min)
                return self._make_dto(
                    code_orig, param, min_val, max_val, text,
                    canonical_code=code_lower, stats=stats or ["item_numsockets"],
                    label=self.label_from_template(tpl),
                    numeric_values=self._parse_numeric_values(actual_min, actual_max),
                )

        if code_lower == "indestruct" or func1 == "20":
            tpl = self._loc("ModStre9s")
            if tpl:
                return self._make_dto(
                    code_orig, param, min_val, max_val, tpl,
                    canonical_code=code_lower, stats=stats or ["item_indesctructible"],
                    label=self.label_from_template(tpl), numeric_values=num_vals,
                )

        if code_lower == "ethereal" or func1 == "23":
            tpl = self._loc("Strethereal")
            if tpl:
                return self._make_dto(
                    code_orig, param, min_val, max_val, tpl,
                    canonical_code=code_lower, stats=stats or ["ethereal"],
                    label=self.label_from_template(tpl), numeric_values=num_vals,
                )

        if code_lower == "bloody" or prop.get("stat1") == "item_extrablood":
            tpl = self._loc("ModStr5p") or "Extra Blood"
            return self._make_dto(
                code_orig, param, min_val, max_val, tpl,
                canonical_code=code_lower, stats=stats or ["item_extrablood"],
                label=self.label_from_template(tpl), numeric_values=num_vals,
            )

        if code_lower == "abs-pois/lvl":
            tpl = self._loc("ModStre9r")
            s2 = self._loc("ModStre9c")
            if tpl:
                p_min = v_min / 8
                p_max = self._parse_int(actual_max, v_min) / 8
                p_range = self._format_decimal(p_min) if p_min == p_max else f"{self._format_decimal(p_min)}-{self._format_decimal(p_max)}"
                text = self._substitute_numeric(tpl, p_range, 1 if p_min >= 0 else -1)
                label = self.label_from_template(tpl)
                if s2:
                    text = f"{text} {s2}"
                    label = f"{label} {s2}"
                return self._make_dto(
                    code_orig, param, min_val, max_val, text,
                    canonical_code=code_lower, stats=stats or ["item_absorb_pois_perlevel"],
                    label=label, numeric_values=[p_min] if p_min == p_max else [p_min, p_max],
                )

        if code_lower == "abs-pois/time":
            tpl = self._loc("ModStre9r")
            if tpl:
                base_text = self._substitute_numeric(tpl, range_str, v_min)
                wrapper = self._loc(_TIME_WRAPPER_KEYS.get(str(param).strip(), "ModStre9d"))
                text = wrapper.replace("%s", base_text) if wrapper and "%s" in wrapper else base_text
                return self._make_dto(
                    code_orig, param, min_val, max_val, text,
                    canonical_code=code_lower, stats=stats or ["item_absorb_pois_bytime"],
                    label=self.label_from_template(tpl), numeric_values=num_vals, parameter_key=str(param).strip(),
                )

        return None

    def _resolve_cold_length(
        self,
        code_orig: str,
        param: str,
        min_val: str,
        max_val: str,
        actual_min: str,
        actual_max: str,
        stats: List[str],
    ) -> PropertyDTO:
        try:
            min_f = int(actual_min)
            max_f = int(actual_max or actual_min)
        except (TypeError, ValueError):
            dur_text = self._format_frame_duration(actual_min, actual_max)
            return self._make_dto(
                code_orig, param, min_val, max_val, f"Cold Duration: {dur_text}",
                canonical_code="cold-len", stats=stats or ["coldlength"], label="Cold Duration",
                numeric_values=self._parse_numeric_values(actual_min, actual_max),
            )
        singular_tpl = self._loc("strskillcoldlengthsingular")
        plural_tpl = self._loc("strskill13")
        if plural_tpl or singular_tpl:
            if min_f == max_f and min_f == 25 and singular_tpl:
                text = self._substitute_numeric(singular_tpl, "1", 1)
                label = self.label_from_template(singular_tpl)
            elif plural_tpl:
                min_s = self._format_decimal(min_f / 25)
                max_s = self._format_decimal(max_f / 25)
                sec_range = min_s if min_f == max_f else f"{min_s}-{max_s}"
                text = self._substitute_numeric(plural_tpl, sec_range, 1)
                label = self.label_from_template(plural_tpl)
            else:
                text = self._substitute_numeric(singular_tpl, self._format_decimal(min_f / 25), 1)
                label = self.label_from_template(singular_tpl)
            return self._make_dto(
                code_orig, param, min_val, max_val, text,
                canonical_code="cold-len", stats=stats or ["coldlength"], label=label,
                numeric_values=[float(min_f)] if min_f == max_f else [float(min_f), float(max_f)],
            )
        dur_text = self._format_frame_duration(actual_min, actual_max)
        return self._make_dto(
            code_orig, param, min_val, max_val, f"Cold Duration: {dur_text}",
            canonical_code="cold-len", stats=stats or ["coldlength"], label="Cold Duration",
            numeric_values=[float(min_f)] if min_f == max_f else [float(min_f), float(max_f)],
        )

    def _format_group_options(self, options: List[str], pick_mode: str) -> str:
        if len(options) <= 1 or pick_mode == "1":
            return " / ".join(options)
        header_tpl = self._loc("chroniclePropertyGroupListHeader")
        if header_tpl and "%s" in header_tpl:
            header = header_tpl.replace("%s", "1")
            return f"{header} {' / '.join(options)}"
        return f" (Random: {' OR '.join(options)})"

    def resolve_property(self, code: str, param: str, min_val: str, max_val: str) -> PropertyDTO:
        code_orig = code
        code_lower = code.strip().lower()

        if not code_lower or code_lower == "xxx" or code_lower.startswith("*"):
            return self._make_dto(code, param, min_val, max_val, "", canonical_code=code_lower)

        # 1. Property Groups (with per-repo data support)
        if code_lower in self.property_groups:
            group = self.property_groups[code_lower]
            pick_mode = group.get("PickMode", "1")
            options: List[PropertyDTO] = []
            for i in range(1, 9):
                p_code = group.get(f"Prop{i}", "").strip()
                if p_code and p_code != "xxx":
                    res = self.resolve_property(
                        p_code,
                        group.get(f"ParMin{i}", ""),
                        group.get(f"ModMin{i}", ""),
                        group.get(f"ModMax{i}", ""),
                    )
                    options.append(res)
            if len(options) == 1:
                child = options[0]
                return self._make_dto(
                    code_orig, param, min_val, max_val, child["resolved_text"],
                    canonical_code=child.get("canonical_code", code_lower),
                    stats=child.get("stats", []),
                    label=child.get("label", ""),
                    numeric_values=child.get("numeric_values", []),
                    parameter_key=child.get("parameter_key", ""),
                )
            text = self._format_group_options([opt["resolved_text"] for opt in options], pick_mode)
            group_stats = [s for opt in options for s in opt.get("stats", [])]
            group_nums = [n for opt in options for n in opt.get("numeric_values", [])]
            group_label = " / ".join(dict.fromkeys(opt.get("label", "") for opt in options if opt.get("label")))
            return self._make_dto(
                code_orig, param, min_val, max_val, text,
                canonical_code=code_lower, stats=group_stats, label=group_label, numeric_values=group_nums,
            )

        prop = self.properties.get(code_lower)
        if not prop:
            if code_lower in _MISSING_PROPERTY_GROUP_FALLBACKS:
                fb_text = _MISSING_PROPERTY_GROUP_FALLBACKS[code_lower]
                range_str = self._range_text(min_val, max_val)
                resolved = f"{fb_text} ({range_str})" if range_str else fb_text
                return self._make_dto(
                    code_orig, param, min_val, max_val, resolved,
                    canonical_code=code_lower, stats=[code_lower],
                    label=fb_text, numeric_values=self._parse_numeric_values(min_val, max_val),
                )
            return self._make_dto(
                code_orig, param, min_val, max_val, f"Unknown property ({code_orig})",
                canonical_code=code_lower, stats=[code_lower],
                label=f"Unknown property ({code_orig})",
                numeric_values=self._parse_numeric_values(min_val, max_val),
                is_unknown=True,
            )

        func1 = prop.get("func1", "0").strip()
        actual_min, actual_max = min_val, max_val
        if (func1 in {"14", "17"} or code_lower == "dmg-ac") and not actual_min and param:
            actual_min, actual_max = param, param
        range_str = self._range_text(actual_min, actual_max)
        stats = self._stat_meta(prop)

        # 2. Engine-native properties & specialized localization keys
        native_dto = self._resolve_engine_native(
            code_orig, code_lower, prop, param, min_val, max_val, actual_min, actual_max, range_str
        )
        if native_dto is not None:
            return native_dto

        # 3. Grouped itemstatcost display (dgrp) when all stats belong to the same display group
        stat_rows = [self.stats[st.lower()] for st in stats if st.lower() in self.stats]
        if len(stat_rows) > 1:
            dgrp_ids = {row.get("dgrp", "").strip() for row in stat_rows}
            if len(dgrp_ids) == 1 and "" not in dgrp_ids:
                first_row = stat_rows[0]
                if first_row.get("dgrpstrpos", "").strip():
                    dgrp_res = self._format_stat_entry(first_row, actual_min, actual_max, param, use_dgrp=True)
                    if dgrp_res:
                        text, label, num_vals, param_key = dgrp_res
                        return self._make_dto(
                            code_orig, param, min_val, max_val, text,
                            canonical_code=code_lower, stats=stats, label=label,
                            numeric_values=num_vals, parameter_key=param_key,
                        )

        # 4. Primary itemstatcost.txt descfunc / descstrpos path across stat1..stat7
        resolved_parts: List[Tuple[str, str, List[float], str]] = []
        seen_texts: set[str] = set()
        for stat_row in stat_rows:
            entry = self._format_stat_entry(stat_row, actual_min, actual_max, param, use_dgrp=False)
            if entry and entry[0] not in seen_texts:
                seen_texts.add(entry[0])
                resolved_parts.append(entry)
        if resolved_parts:
            if len(resolved_parts) == 1:
                text, label, num_vals, param_key = resolved_parts[0]
            else:
                text = " / ".join(part[0] for part in resolved_parts)
                label = " / ".join(dict.fromkeys(part[1] for part in resolved_parts if part[1]))
                num_vals = resolved_parts[0][2]
                param_key = next((part[3] for part in resolved_parts if part[3]), "")
            return self._make_dto(
                code_orig, param, min_val, max_val, text,
                canonical_code=code_lower, stats=stats, label=label,
                numeric_values=num_vals, parameter_key=param_key,
            )

        # 5. Last-resort *Tooltip fallback ONLY when itemstatcost/localization yielded nothing
        tooltip_dto = self._resolve_tooltip_fallback(
            code_orig, code_lower, prop, param, min_val, max_val, actual_min, actual_max, range_str
        )
        if tooltip_dto is not None:
            return tooltip_dto

        # 6. Skill code fallback when skills.txt is missing or itemstatcost wasn't localized
        skill_codes = {
            "oskill", "skill", "att-skill", "hit-skill", "gethit-skill",
            "kill-skill", "death-skill", "levelup-skill", "aura",
        }
        if code_lower in skill_codes:
            skill_name = self.resolve_skill_name(param)
            templates = {
                "oskill": f"+{range_str} to {skill_name}",
                "skill": f"+{range_str} to {skill_name}",
                "aura": f"Level {range_str} {skill_name} Aura When Equipped",
                "hit-skill": f"{min_val}% Chance to cast Level {max_val} {skill_name} on striking",
                "att-skill": f"{min_val}% Chance to cast Level {max_val} {skill_name} on attack",
                "gethit-skill": f"{min_val}% Chance to cast Level {max_val} {skill_name} when struck",
                "kill-skill": f"{min_val}% Chance to cast Level {max_val} {skill_name} when you Kill an Enemy",
                "death-skill": f"{min_val}% Chance to cast Level {max_val} {skill_name} when you Die",
                "levelup-skill": f"{min_val}% Chance to cast Level {max_val} {skill_name} when you Level-Up",
            }
            text = templates[code_lower]
            return self._make_dto(
                code_orig, param, min_val, max_val, text,
                canonical_code=code_lower, stats=stats or [code_lower],
                label=self.label_from_template(text, protected_names=[skill_name]),
                numeric_values=self._parse_numeric_values(min_val, max_val),
                parameter_key=str(param).strip(),
            )

        # 7. Final code-name string lookup
        localized_code = self._loc(code_orig) or self._loc(code_orig.capitalize())
        if localized_code:
            text = f"{localized_code}: {range_str}" if range_str else localized_code
            return self._make_dto(
                code_orig, param, min_val, max_val, text,
                canonical_code=code_lower, stats=stats or [code_lower],
                label=localized_code, numeric_values=self._parse_numeric_values(actual_min, actual_max),
            )

        return self._make_dto(
            code_orig, param, min_val, max_val, f"Unknown property ({code_orig})",
            canonical_code=code_lower, stats=stats or [code_lower],
            label=f"Unknown property ({code_orig})",
            numeric_values=self._parse_numeric_values(actual_min, actual_max),
            is_unknown=True,
        )

    def cold_duration(
        self, code: str, param: str, min_val: str, max_val: str,
    ) -> Optional[Tuple[int, int, bool]]:
        """Return the duration bounds and set/add flag for a cold modifier."""
        if code not in {"dmg-cold", "cold-len"}:
            return None
        definition = self.properties.get(code, {})
        default_slot = 3 if code == "dmg-cold" else 1
        slot = next(
            (index for index in range(1, 8) if definition.get(f"stat{index}") == "coldlength"),
            default_slot,
        )
        function = definition.get(f"func{slot}") or ("17" if code == "dmg-cold" else "1")
        try:
            if function == "17" and int(param or "0"):
                low = high = int(param)
            else:
                low, high = sorted((int(min_val or "0"), int(max_val or min_val or "0")))
        except ValueError:
            return None
        if low == high == 0:
            return None
        return low, high, definition.get(f"set{slot}") == "1"

    def _format_frame_duration(self, min_val: str, max_val: str) -> str:
        def parse_frames(raw: str) -> Optional[int]:
            try:
                return int(raw)
            except (TypeError, ValueError):
                return None

        min_frames = parse_frames(min_val)
        max_frames = parse_frames(max_val)
        if min_frames is None and max_frames is None:
            return f"{min_val}-{max_val} frames" if min_val != max_val else f"{min_val} frames"
        if max_frames is None:
            max_frames = min_frames
        if min_frames is None:
            min_frames = max_frames

        def seconds_text(frames: int) -> str:
            seconds = frames / 25
            return str(int(seconds)) if seconds.is_integer() else f"{seconds:.2f}".rstrip("0").rstrip(".")

        if min_frames == max_frames:
            unit = "second" if min_frames == 25 else "seconds"
            return f"{seconds_text(min_frames)} {unit} ({min_frames} frames)"
        return f"{seconds_text(min_frames)}-{seconds_text(max_frames)} seconds ({min_frames}-{max_frames} frames)"
