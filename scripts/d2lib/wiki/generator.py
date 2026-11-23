from __future__ import annotations
from d2lib.services.item_types import ItemTypeTaxonomy
import json
import html
import os
import re
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlencode

from d2lib.repository import (
    D2Repository,
    D2RepositoryProtocol,
    resolve_difficulty_name,
    resolve_localized_string,
)
from d2lib.services import (
    PropertyResolverService,
    BaseItemAnalyzerService,
    CubeAnalyzerService,
    MonsterAnalyzerService,
    MiscAnalyzerService,
    MechanicsAnalyzerService,
    DropSourceAnalyzerService,
    ReferenceAnalyzerService,
)
from d2lib.services.resolver import load_property_groups
from d2lib.services.skill_comparison import SkillComparisonService
from d2lib.services.recipes import RecipePresentationBuilder
from d2lib.models import (
    BaseItemFamilyDTO,
    CubeRecipeGroupDTO,
    MonsterActGroupDTO,
    MiscGroupDTO,
    MechanicsSummaryDTO,
    SetFamilyDTO,
    MiscItemDTO,
)
from d2lib.utils import slugify
from d2lib.wiki.routes import ITEM_FAMILIES, REPORT_SOURCES, WikiRoutes
from d2lib.wiki.renderers import HtmlWikiRenderer, WikiPublisher, highlight_comparison
from d2lib.wiki.publication import WikiSiteDTO, WikiSiteRecordingWriter, empty_wiki_site
from d2lib.wiki.history import HistoryCollector, item_history
from d2lib.wiki.history_comparison import write_history_comparisons
from pathlib import Path
from d2lib.wiki.builders import AreaFarmingDataBuilder, ItemIconExporter
from d2lib.wiki.affix_functions import AFFIX_FUNCTIONS_SLUG, affix_function_groups
from d2lib.wiki.comparison import (
    affix_card_contexts,
    skill_card_context,
    item_diff_status,
    property_occurrence_map,
    rune_property_occurrence_map,
    item_comparison_context,
    base_item_comparison_context,
    gem_rune_comparison_context,
    set_bonus_comparison,
)
from d2lib.wiki.item_helpers import (
    item_filter_group,
    item_filter_type,
    should_include_item,
    item_sort_key,
    item_identity,
    item_title,
    item_summary,
    item_search_text,
    set_item_anchor,
)

MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
D2LIB_DIR = os.path.dirname(MODULE_DIR)
REPO_ROOT = os.path.abspath(os.path.join(D2LIB_DIR, "..", ".."))


class WikiContentBuilder:
    def __init__(
        self,
        item_db_dir: str,
        skill_tree_dir: str,
        output_dir: str,
        old_item_db_dir: Optional[str] = None,
        old_label: str = "Retail",
        new_label: str = "BKDiablo",
        game_data_dir: Optional[str] = None,
        retail_data_dir: Optional[str] = None,
        layout_data_dir: Optional[str] = None,
        locale: str = "enUS",
    ):
        self.item_db_dir = item_db_dir
        self.skill_tree_dir = skill_tree_dir
        self.output_dir = output_dir
        self.old_item_db_dir = old_item_db_dir
        self.old_label = old_label
        self.new_label = new_label
        self.game_data_dir = game_data_dir or os.path.join(REPO_ROOT, "mods", "BKDiablo", "bkdiablo.mpq")
        self.retail_data_dir = retail_data_dir or os.path.join(REPO_ROOT, "data", "retail")
        self.layout_data_dir = layout_data_dir
        self.locale = str(locale or "enUS").strip() or "enUS"
        self.site: WikiSiteDTO = empty_wiki_site(old_label, new_label, locale=self.locale)
        self.writer = WikiSiteRecordingWriter(self.site)
        self.manifest = self.site["manifest"]
        self._repo: Optional[D2Repository] = None
        self._retail_repo: Optional[D2Repository] = None

    def build(self) -> WikiSiteDTO:
        self.site = empty_wiki_site(self.old_label, self.new_label, locale=self.locale)
        self.writer = WikiSiteRecordingWriter(self.site)
        self.manifest = self.site["manifest"]

        # Cached repos — all _load_* and _write_* methods share these instances.
        self._repo = D2Repository(self.game_data_dir, locale=self.locale)
        self._taxonomy = ItemTypeTaxonomy(self._repo)
        self._retail_repo = D2Repository(self.retail_data_dir, locale=self.locale)

        history_config = json.loads(Path(REPO_ROOT, "data", "item-history.json").read_text(encoding="utf-8"))
        history_collector = HistoryCollector(self.game_data_dir, Path(REPO_ROOT, ".cache", "item-history"), history_config)
        self._history = history_collector.collect()
        self._history_aliases = history_config.get("aliases", {})
        self.writer.write_text("data/item-history.json", json.dumps(self._history, ensure_ascii=True))
        items = self._load_items()
        for family, entries in items.items():
            for entry in entries:
                entry["history"] = item_history(self._history, family, entry.get("raw_row", {}), self._history_aliases)
        old_items = (
            self._load_items(self.old_item_db_dir)
            if self.old_item_db_dir
            else {family: [] for family in ITEM_FAMILIES}
        )
        old_item_index = self._index_items(old_items)
        class_pages = self._load_class_pages()
        area_entries = self._load_area_entries()
        base_item_families = self._load_base_item_families()
        base_item_lookup = {item["code"]: item for family in base_item_families for item in family["members"]}
        retail_base_items = self._load_retail_base_items()
        misc_groups, gem_rune_groups = self._load_misc_groups()
        retail_misc_items = self._load_retail_misc_items()
        write_history_comparisons(history_collector, self._history, self._repo, items, old_item_index,
                                  base_item_families, retail_base_items, gem_rune_groups, retail_misc_items,
                                  self.writer, self.old_label, self._retail_repo)

        # Single CubeAnalyzerService for both group summary and raw recipes.
        recipe_service = CubeAnalyzerService(self._repo, self._retail_repo)
        recipe_groups = recipe_service.analyze_all_recipes()
        raw_recipes = recipe_service.analyze_raw_recipes(include_removed=True)
        recipe_pages_data = RecipePresentationBuilder(recipe_service, raw_recipes, recipe_groups).build()

        monster_groups = self._load_monster_groups()
        mechanics_summary = self._load_mechanics_summary()
        mercenary_data = self._load_mercenary_data()
        drop_weight_groups = self._load_drop_weight_groups()
        drop_source_data = self._load_drop_source_data()
        reference_pages, reference_coverage = self._load_reference_pages()

        self._write_assets()
        item_entries = self._write_item_pages(items, old_item_index, base_item_lookup, retail_base_items)
        class_entries = self._write_class_pages(class_pages)
        self._write_runeword_index_page(items["runeword"], item_entries["runeword"], old_item_index)
        self._write_set_index_page(items["set"], old_item_index["set"], base_item_lookup, retail_base_items)
        self._write_base_item_pages(base_item_families, retail_base_items)
        self._write_recipe_pages(recipe_groups, recipe_pages_data)
        self._write_bestiary_pages(monster_groups)
        self._write_misc_pages(misc_groups)
        self._write_gems_runes_pages(gem_rune_groups, retail_misc_items)
        self._write_mechanics_pages(mechanics_summary)
        self._write_mercenary_pages(mercenary_data)
        self._write_drop_weight_pages(drop_weight_groups)
        self._write_drop_source_pages(drop_source_data)
        self._write_reference_pages(reference_pages, reference_coverage)
        report_entries = self._publish_reports()
        self._write_indexes(item_entries, class_entries, report_entries, area_entries, base_item_families, recipe_groups, monster_groups, misc_groups, gem_rune_groups, drop_weight_groups, reference_pages)
        self._write_patch_notes_draft(item_entries, class_entries)
        self._write_item_index_data(item_entries, items)
        self._write_area_index_data(area_entries)
        self._write_manifest()
        return self.site

    # ── Data loaders ────────────────────────────────────────────────────────

    def _load_base_item_families(self) -> List[BaseItemFamilyDTO]:
        resolver = PropertyResolverService(self._repo)
        return BaseItemAnalyzerService(self._repo, resolver).analyze_base_items()

    def _load_retail_base_items(self) -> Dict[str, Any]:
        retail_resolver = PropertyResolverService(self._retail_repo)
        retail_families = BaseItemAnalyzerService(self._retail_repo, retail_resolver).analyze_base_items()
        return {item["code"]: item for f in retail_families for item in f["members"]}

    def _load_monster_groups(self) -> List[MonsterActGroupDTO]:
        return MonsterAnalyzerService(self._repo, self._retail_repo).analyze_monsters()

    def _load_retail_misc_items(self) -> Dict[str, Any]:
        return {item["code"]: item for g in MiscAnalyzerService(self._retail_repo).analyze_misc_items() for item in g["members"]}

    def _load_misc_groups(self) -> Tuple[List[MiscGroupDTO], List[MiscGroupDTO]]:
        resolver = PropertyResolverService(self._repo)
        groups = MiscAnalyzerService(self._repo, resolver, self._retail_repo).analyze_misc_items()
        for group in groups:
            for member in group["members"]:
                member["history"] = item_history(self._history, "base", member, self._history_aliases)
        gem_rune_keys = {"runes", "gems"}
        gem_rune_groups = [g for g in groups if g.get("category_key") in gem_rune_keys]
        material_groups = [g for g in groups if g.get("category_key") not in gem_rune_keys]
        return material_groups, gem_rune_groups

    def _load_mechanics_summary(self) -> MechanicsSummaryDTO:
        return MechanicsAnalyzerService(self._repo, self._retail_repo).analyze_mechanics()

    @staticmethod
    def _safe_excel_table(repo: Any, table_name: str) -> List[Dict[str, str]]:
        getter = getattr(repo, "get_excel_table", None)
        if not callable(getter):
            return []
        try:
            rows = getter(table_name)
        except Exception:
            return []
        return rows if isinstance(rows, list) else []

    @classmethod
    def _mercenary_repo_context(cls, repo: Any) -> Tuple[Dict[str, str], Optional[PropertyResolverService]]:
        monstats_by_idx: Dict[str, str] = {}
        for row in cls._safe_excel_table(repo, "monstats"):
            idx = str(row.get("*hcIdx", "")).strip()
            namestr = str(row.get("NameStr", "")).strip()
            if idx and namestr and idx not in monstats_by_idx:
                monstats_by_idx[idx] = namestr
        resolver: Optional[PropertyResolverService] = None
        if callable(getattr(repo, "get_excel_table", None)):
            try:
                skills_rows = repo.get_excel_table("skills")
                if isinstance(skills_rows, list):
                    resolver = PropertyResolverService(repo)
            except Exception:
                resolver = None
        return monstats_by_idx, resolver

    @staticmethod
    def _mercenary_row_meta(
        row: Dict[str, str],
        repo: Any,
        monstats_by_idx: Dict[str, str],
        resolver: Optional[PropertyResolverService],
    ) -> Dict[str, Any]:
        act_raw = str(row.get("Act", "")).strip()
        act = int(act_raw) if act_raw.isdigit() else 99
        class_id = str(row.get("Class", "")).strip()
        diff_raw = str(row.get("Difficulty", "")).strip()
        raw_sub = str(row.get("*SubType", "")).strip()
        sub_part, sep, diff_part = raw_sub.rpartition("-")
        legacy_diff_map = {"normal": "1", "nightmare": "2", "hell": "3"}
        if not diff_raw and sep:
            diff_raw = legacy_diff_map.get(diff_part.strip().casefold(), "")
        difficulty_id = diff_raw if diff_raw in {"1", "2", "3"} else ""
        difficulty_slug = {
            "1": "normal",
            "2": "nightmare",
            "3": "hell",
        }.get(difficulty_id, slugify(diff_part or diff_raw) if (diff_part or diff_raw) else "")
        difficulty = resolve_difficulty_name(repo, difficulty_id or diff_raw)

        namestr = monstats_by_idx.get(class_id, "")
        hireling_raw = str(row.get("Hireling", "")).strip()
        canonical_group = namestr or hireling_raw
        group_name = (
            resolve_localized_string(repo, namestr)
            or resolve_localized_string(repo, hireling_raw)
            or canonical_group
        )

        def skill_display(skill_code: str) -> str:
            if not skill_code:
                return ""
            if resolver is not None:
                resolved = resolver.resolve_skill_name(skill_code)
                if resolved:
                    return resolved
            return resolve_localized_string(repo, skill_code) or skill_code

        hire_desc = str(row.get("HireDesc", "")).strip()
        skill1 = str(row.get("Skill1", "")).strip()
        if hire_desc:
            variant_key = hire_desc.casefold()
            variant = resolve_localized_string(repo, hire_desc) or hire_desc
        elif skill1:
            variant_key = skill1.casefold()
            variant = skill_display(skill1)
        else:
            legacy_sub = sub_part.strip() if sep else raw_sub
            variant_key = legacy_sub.casefold()
            variant = resolve_localized_string(repo, legacy_sub) or legacy_sub

        skills_map = {
            f"Skill{i}": skill_display(str(row.get(f"Skill{i}", "")).strip())
            for i in range(1, 7)
            if str(row.get(f"Skill{i}", "")).strip()
        }
        return {
            "act": act,
            "class_id": class_id,
            "canonical_group": canonical_group,
            "name": group_name,
            "variant_key": variant_key,
            "variant": variant,
            "difficulty_id": difficulty_id,
            "difficulty_slug": difficulty_slug,
            "difficulty": difficulty,
            "skills_map": skills_map,
        }

    def _load_mercenary_data(self) -> Dict[str, Any]:
        fields = ("HP", "HP/Lvl", "Defense", "Def/Lvl", "Str", "Str/Lvl", "Dex", "Dex/Lvl",
                  "AR", "AR/Lvl", "Dmg-Min", "Dmg-Max", "Dmg/Lvl", "DefaultChance",
                  "ResistFire", "ResistFire/Lvl", "ResistCold", "ResistCold/Lvl",
                  "ResistLightning", "ResistLightning/Lvl", "ResistPoison", "ResistPoison/Lvl")
        skill_fields = tuple(
            f"{field}{i}" for i in range(1, 7)
            for field in ("Skill", "Mode", "Chance", "ChancePerLvl", "Level", "LvlPerLvl")
        )

        def load(repo):
            monstats_by_idx, resolver = self._mercenary_repo_context(repo)
            result: Dict[Tuple[int, str, str, str, str], Tuple[Dict[str, str], Dict[str, Any]]] = {}
            for row in self._safe_excel_table(repo, "hireling"):
                if row.get("Version") != "100":
                    continue
                if not (row.get("Class") or row.get("Hireling")):
                    continue
                level = str(row.get("Level", "")).strip()
                if not level.isdigit():
                    continue
                meta = self._mercenary_row_meta(row, repo, monstats_by_idx, resolver)
                group_key = meta["class_id"] or meta["canonical_group"].casefold()
                key = (meta["act"], group_key, meta["variant_key"], meta["difficulty_id"], level)
                result.setdefault(key, (row, meta))
            return result

        current, retail = load(self._repo), load(self._retail_repo)
        entries = []

        def key_sort(item_key: Tuple[int, str, str, str, str]) -> Tuple[int, str, str, int, int]:
            act_num, group_id, variant_k, diff_id, lvl = item_key
            return (act_num, group_id, variant_k, int(diff_id) if diff_id.isdigit() else 99, int(lvl))

        for key in sorted(set(current) | set(retail), key=key_sort):
            cur_pair = current.get(key)
            ret_pair = retail.get(key)
            row = cur_pair[0] if cur_pair else None
            old = ret_pair[0] if ret_pair else None
            meta = (cur_pair or ret_pair)[1]
            cur_skills = cur_pair[1]["skills_map"] if cur_pair else {}
            ret_skills = ret_pair[1]["skills_map"] if ret_pair else {}
            changed = [field for field in fields + skill_fields if row and old and row.get(field, "") != old.get(field, "")]
            entries.append({
                "act": meta["act"],
                "class_id": meta["class_id"],
                "canonical_group": meta["canonical_group"],
                "name": meta["name"],
                "variant_key": meta["variant_key"],
                "variant": meta["variant"],
                "difficulty_id": meta["difficulty_id"],
                "difficulty_slug": meta["difficulty_slug"],
                "difficulty": meta["difficulty"],
                "level": key[4],
                "status": "added" if row and not old else "removed" if old and not row else "changed" if changed else "unchanged",
                "current": row or {},
                "retail": old or {},
                "current_skills": cur_skills,
                "retail_skills": ret_skills,
                "changed_fields": changed,
            })
        return {"rows": entries, "summary": {"total": len(entries), "changed": sum(r["status"] != "unchanged" for r in entries), "added": sum(r["status"] == "added" for r in entries), "removed": sum(r["status"] == "removed" for r in entries)}}

    @staticmethod
    def _mercenary_stats_at_level(source: Dict[str, str], level: int) -> Dict[str, str]:
        """Apply hireling growth units to one expansion progression breakpoint.

        Formula reference: https://locbones.github.io/D2R_DataGuide/#hirelingtxt
        Resistance values are raw, before difficulty penalties and caps.
        """
        if not source:
            return {}
        result = dict(source)
        delta = level - int(source["Level"])
        if delta < 0:
            raise ValueError("Target level precedes the hireling breakpoint")
        growth = [("HP", "HP/Lvl", 1), ("Defense", "Def/Lvl", 1),
                  ("AR", "AR/Lvl", 1), ("Str", "Str/Lvl", 8), ("Dex", "Dex/Lvl", 8),
                  ("Dmg-Min", "Dmg/Lvl", 8), ("Dmg-Max", "Dmg/Lvl", 8)]
        growth += [(f"Resist{element}", f"Resist{element}/Lvl", 4)
                   for element in ("Fire", "Cold", "Lightning", "Poison")]
        for i in range(1, 7):
            if source.get(f"Skill{i}"):
                growth.extend([(f"Level{i}", f"LvlPerLvl{i}", 32),
                               (f"Chance{i}", f"ChancePerLvl{i}", 4)])
        for field, rate, divisor in growth:
            if source.get(field, "") != "":
                result[field] = str(int(source[field]) + delta * int(source.get(rate) or 0) // divisor)
        result["Level"] = str(level)
        return result

    def _write_mercenary_pages(self, data: Dict[str, Any]) -> None:
        by_type: Dict[Tuple[int, str, str], List[Dict[str, Any]]] = {}
        for row in data["rows"]:
            type_key = (
                int(row.get("act", 99)),
                str(row.get("class_id") or row.get("canonical_group") or row["name"]).casefold(),
                str(row.get("variant_key") or row["variant"]).casefold(),
            )
            by_type.setdefault(type_key, []).append(row)

        entries = []
        used_slugs: set[str] = set()

        def type_order(item: Tuple[Tuple[int, str, str], List[Dict[str, Any]]]) -> Tuple[int, str, str, str]:
            (act_num, class_key, _), rows = item
            first = rows[0]
            return (act_num, first["name"].casefold(), first["variant"].casefold(), class_key)

        for (act_num, class_key, _), type_rows in sorted(by_type.items(), key=type_order):
            type_rows.sort(
                key=lambda r: (
                    int(r["difficulty_id"]) if str(r.get("difficulty_id", "")).isdigit() else 99,
                    int(r["level"] or 0),
                )
            )
            first = type_rows[0]
            canonical_group = first.get("canonical_group") or first["name"]
            variant_key = first.get("variant_key") or first["variant"]
            base_slug = slugify(f"{canonical_group}-{variant_key}")
            slug = base_slug
            if slug in used_slugs:
                suffix = slugify(class_key) if class_key else str(len(used_slugs) + 1)
                slug = f"{base_slug}-{suffix}"
            used_slugs.add(slug)

            offers = []
            by_difficulty: Dict[Tuple[str, str, str], List[Dict[str, Any]]] = {}
            for row in type_rows:
                diff_key = (
                    str(row.get("difficulty_id", "")),
                    str(row.get("difficulty_slug", "")),
                    str(row.get("difficulty", "")),
                )
                by_difficulty.setdefault(diff_key, []).append(row)

            def diff_sort(item: Tuple[Tuple[str, str, str], List[Dict[str, Any]]]) -> Tuple[int, str]:
                diff_id, diff_slug, _ = item[0]
                return (int(diff_id) if diff_id.isdigit() else 99, diff_slug)

            for (diff_id, diff_slug, diff_label), diff_rows in sorted(by_difficulty.items(), key=diff_sort):
                if diff_slug:
                    diff_page_slug = slugify(f"{slug}-{diff_slug}")
                    self._write_page(
                        title=f"{first['name']} ({first['variant']} - {diff_label}) | {self.new_label} Wiki",
                        output_path=WikiRoutes.mercenary_output_path(diff_page_slug),
                        template_name="mercenary.html",
                        category="detail",
                        source_files=[],
                        mercenary={
                            "name": first["name"],
                            "variant": f"{first['variant']} - {diff_label}" if diff_label else first["variant"],
                            "rows": diff_rows,
                        },
                    )
                skills = list(dict.fromkeys(
                    r.get("current_skills", {}).get(f"Skill{i}") or r["current"].get(f"Skill{i}", "")
                    for r in diff_rows for i in range(1, 7)
                    if r["current"].get(f"Skill{i}", "")
                ))
                raw_skills = list(dict.fromkeys(
                    r["current"].get(f"Skill{i}", "")
                    for r in diff_rows for i in range(1, 7)
                    if r["current"].get(f"Skill{i}", "")
                ))
                offers.append({
                    "difficulty": diff_label,
                    "difficulty_id": diff_id,
                    "skills": skills,
                    "raw_skills": raw_skills,
                    "available": any(r["current"] for r in diff_rows),
                })

            chosen_row = min(
                (r for r in type_rows if r["current"]),
                key=lambda r: {"3": 0, "2": 1, "1": 2}.get(str(r.get("difficulty_id", "")), 3),
                default=type_rows[0],
            )
            chosen_diff_id = str(chosen_row.get("difficulty_id", ""))
            chosen_diff_label = chosen_row.get("difficulty", "")
            preview: Dict[str, Any] = {
                "level": "80",
                "difficulty": chosen_diff_label,
                "difficulty_id": chosen_diff_id,
                "current_skills": {},
                "retail_skills": {},
            }
            for side in ("current", "retail"):
                candidates = [
                    r for r in type_rows
                    if str(r.get("difficulty_id", "")) == chosen_diff_id
                    and r[side]
                    and int(r[side]["Level"]) <= 80
                ]
                source_entry = max(candidates, key=lambda r: int(r[side]["Level"]), default=None)
                if source_entry:
                    preview[side] = self._mercenary_stats_at_level(source_entry[side], 80)
                    preview[f"{side}_skills"] = dict(source_entry.get(f"{side}_skills", {}))
                else:
                    preview[side] = {}

            changed = any(r["status"] != "unchanged" for r in type_rows)
            entry = {
                "act": act_num,
                "class_id": first.get("class_id", ""),
                "name": first["name"],
                "variant": first["variant"],
                "slug": slug,
                "levels": len(type_rows),
                "rows": type_rows,
                "offers": offers,
                "status": "changed" if changed else "unchanged",
                "preview": preview,
            }
            entries.append(entry)
            self._write_page(
                title=f"{entry['name']} ({entry['variant']}) | {self.new_label} Wiki",
                output_path=WikiRoutes.mercenary_output_path(entry["slug"]),
                template_name="mercenary.html",
                category="detail",
                source_files=[],
                mercenary=entry,
            )

        grouped_map: Dict[Tuple[int, str], List[Dict[str, Any]]] = {}
        for entry in entries:
            grouped_map.setdefault((entry["act"], entry["name"]), []).append(entry)
        groups = [
            {"act": act_num, "name": group_name, "entries": group_entries}
            for (act_num, group_name), group_entries in sorted(
                grouped_map.items(),
                key=lambda item: (item[0][0], item[0][1].casefold()),
            )
        ]

        self.writer.write_text("data/mercenaries.json", json.dumps(data, indent=2))
        self._write_page(
            title=f"Mercenaries | {self.new_label} Wiki",
            output_path=WikiRoutes.mercenaries_index_output_path(),
            template_name="mercenaries_index.html",
            category="index",
            source_files=[
                os.path.join(self.game_data_dir, "data", "global", "excel", "hireling.txt"),
                os.path.join(self.retail_data_dir, "global", "excel", "hireling.txt"),
            ],
            data=data,
            entries=entries,
            groups=groups,
        )

    def _load_drop_weight_groups(self) -> List[Dict[str, Any]]:
        base_names = self._drop_base_name_lookup(self._repo)
        groups: List[Dict[str, Any]] = []
        groups.extend(self._quality_drop_weight_groups(self._repo.get_excel_table("setitems"), "set", "item", base_names, repo=self._repo))
        groups.extend(self._quality_drop_weight_groups(self._repo.get_excel_table("uniqueitems"), "unique", "code", base_names, repo=self._repo))
        return sorted(groups, key=lambda row: (row["base_name"].lower(), row["quality"], -row["max_chance"]))

    def _load_drop_source_data(self) -> Dict[str, Any]:
        return DropSourceAnalyzerService(self._repo).analyze_drop_sources()

    def _load_reference_pages(self) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        table_names = self._available_excel_tables()
        group_path = os.path.join(REPO_ROOT, "data", "propertygroups.txt")
        property_groups = load_property_groups(self._repo, group_path)
        retail_property_groups = load_property_groups(self._retail_repo, group_path) or property_groups
        service = ReferenceAnalyzerService(self._repo, PropertyResolverService(self._repo, property_groups))
        baseline = ReferenceAnalyzerService(
            self._retail_repo, PropertyResolverService(self._retail_repo, retail_property_groups),
        )
        pages = service.build_pages(table_names, baseline=baseline)
        coverage = service.build_coverage(pages, table_names, self._core_raw_table_coverage())
        affixes = next(page for page in pages if page["slug"] == "affixes")
        groups = affix_function_groups(service)
        pages.insert(pages.index(affixes) + 1, {
            "slug": AFFIX_FUNCTIONS_SLUG,
            "title": "Affixes by Function",
            "description": "Browse spawnable prefixes and suffixes by effect, sorted by roll range.",
            "sections": groups,
            "row_count": sum(len(group["rows"]) for group in groups),
            "source_tables": affixes["source_tables"],
            "search_text": "Affixes by Function effect prefix suffix affix level magicprefix magicsuffix",
        })
        return pages, coverage

    @staticmethod
    def _core_raw_table_coverage() -> Dict[str, str]:
        return {
            "armor": "Items, Bases, and References",
            "automagic": "Bases and References",
            "charstats": "Mechanics",
            "cubemain": "Cube Recipes",
            "difficultylevels": "Mechanics",
            "experience": "Mechanics",
            "gamble": "Mechanics and References",
            "gems": "Gems & Runes",
            "hireling": "References",
            "inventory": "References",
            "itemstatcost": "Properties and Mechanics",
            "itemtypes": "Items, Bases, and Recipes",
            "levels": "Areas and Bestiary",
            "lvlmaze": "Areas and References",
            "lvlprest": "Areas and References",
            "lvlwarp": "Areas and References",
            "magicprefix": "Recipes and References",
            "magicsuffix": "Recipes and References",
            "misc": "Materials, Gems & Runes, and Recipes",
            "missiles": "Skills, Mechanics, and References",
            "monai": "References",
            "monpreset": "Areas and References",
            "monprop": "References",
            "monseq": "References",
            "monstats": "Areas, Bestiary, and Drop Sources",
            "monstats2": "Bestiary and References",
            "monumod": "References",
            "npc": "References",
            "objects": "Areas and References",
            "overlay": "References",
            "properties": "Properties, Recipes, and Mechanics",
            "qualityitems": "Bases",
            "runes": "Runewords, Gems & Runes, and Items",
            "setitems": "Items, Sets, and Drops",
            "sets": "Sets",
            "shrines": "References",
            "skilldesc": "Skills and References",
            "skills": "Skills, Mechanics, and References",
            "states": "References",
            "superuniques": "Drop Sources and References",
            "treasureclassex": "Drop Sources",
            "uniqueitems": "Items and Drops",
            "uniqueprefix": "Raw Coverage",
            "weapons": "Items, Bases, and References",
        }

    def _available_excel_tables(self) -> List[str]:
        excel_dir = os.path.join(self.game_data_dir, "data", "global", "excel")
        if not os.path.isdir(excel_dir):
            return []
        return sorted(
            os.path.splitext(filename)[0]
            for filename in os.listdir(excel_dir)
            if filename.lower().endswith(".txt")
        )

    def _load_items(self, item_db_dir: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        items: Dict[str, List[Dict[str, Any]]] = {family: [] for family in ITEM_FAMILIES}
        source_dir = item_db_dir or self.item_db_dir
        if not source_dir or not os.path.isdir(source_dir):
            return items

        for root, _, files in os.walk(source_dir):
            for filename in files:
                if not filename.endswith(".json"):
                    continue
                full_path = os.path.join(root, filename)
                rel_path = os.path.relpath(full_path, source_dir).replace("\\", "/")
                with open(full_path, "r", encoding="utf-8") as f:
                    payload = json.load(f)

                if rel_path.startswith("uniques/"):
                    family = "unique"
                elif rel_path.startswith("sets/"):
                    family = "set"
                elif rel_path.startswith("runewords/"):
                    family = "runeword"
                else:
                    continue

                for entry in payload:
                    record = dict(entry)
                    record["_source_rel_path"] = rel_path
                    if should_include_item(record, family):
                        items[family].append(record)

        return items

    def _index_items(self, items: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Dict[str, Dict[str, Any]]]:
        index: Dict[str, Dict[str, Dict[str, Any]]] = {family: {} for family in ITEM_FAMILIES}
        for family, entries in items.items():
            for entry in entries:
                index[family][item_identity(entry, family)] = entry
        return index

    def _load_class_pages(self) -> List[Dict[str, Any]]:
        return SkillComparisonService(self._repo, self._retail_repo).class_pages()

    def _load_area_entries(self) -> List[Dict[str, Any]]:
        if not os.path.isdir(self.game_data_dir):
            return []
        return AreaFarmingDataBuilder(self.game_data_dir, layout_data_dir=self.layout_data_dir, repository=self._repo).build()

    # ── Writers ─────────────────────────────────────────────────────────────

    def _write_assets(self) -> None:
        ASSET_SOURCE_DIR = os.path.join(MODULE_DIR, "..", "wiki_assets")
        if not os.path.isdir(ASSET_SOURCE_DIR):
            ASSET_SOURCE_DIR = os.path.join(D2LIB_DIR, "wiki_assets")
        for filename in sorted(os.listdir(ASSET_SOURCE_DIR)):
            source_path = os.path.join(ASSET_SOURCE_DIR, filename)
            if os.path.isfile(source_path):
                self.writer.copy_asset(source_path, f"assets/{filename}")

    def _write_base_item_pages(self, families: List[BaseItemFamilyDTO], retail_items: Dict[str, Any]) -> None:
        icon_exporter = ItemIconExporter(self.writer, self.game_data_dir, self.retail_data_dir, repository=self._repo)
        icon_exporter.attach_base_item_icons(families)

        for family in families:
            for item in family["members"]:
                old_item = retail_items.get(item["code"])
                item["comparison"] = base_item_comparison_context(item, old_item)
                item["href"] = ""
                item["history"] = item_history(self._history, "base", item, self._history_aliases)

        max_base_sockets = max(
            (int(item.get("sockets") or 0) for family in families for item in family["members"]),
            default=0,
        )

        self._write_page(
            title=f"Base Items | {self.new_label} Wiki",
            output_path=WikiRoutes.bases_index_output_path(),
            template_name="bases_index.html",
            category="index",
            source_files=[
                os.path.join(self.game_data_dir, "data", "global", "excel", "armor.txt"),
                os.path.join(self.game_data_dir, "data", "global", "excel", "weapons.txt"),
                os.path.join(self.game_data_dir, "data", "global", "excel", "itemtypes.txt"),
                os.path.join(self.game_data_dir, "data", "global", "excel", "automagic.txt"),
                os.path.join(self.game_data_dir, "data", "global", "excel", "qualityitems.txt"),
            ],
            families=families,
            loot_groups=self._taxonomy.loot_groups(include_accessories=False),
            base_groups=sorted({family["group"] for family in families}),
            base_classes=sorted({cn for family in families for cn in family["class_tags"]}),
            base_tier_options=BaseItemAnalyzerService.tier_options(families),
            base_speed_options=BaseItemAnalyzerService.speed_options(families),
            base_socket_options=list(range(1, max_base_sockets + 1)),
            base_type_categories=sorted({
                cat
                for family in families
                for item in family["members"]
                for cat in item["type_categories"]
            }),
        )

    def _write_recipe_pages(self, groups: List[CubeRecipeGroupDTO], recipe_pages: Dict[str, Any]) -> None:
        self.writer.write_text("data/recipes-overview.json", json.dumps(recipe_pages["overview"], indent=2))
        self.writer.write_text("data/recipes-crafting.json", json.dumps(recipe_pages["crafting"], indent=2))
        self.writer.write_text("data/recipes-all.json", json.dumps(recipe_pages["all"], indent=2))
        self.writer.write_text("data/recipes-raw.json", json.dumps(recipe_pages["raw"], indent=2))

        cubemain_src = [os.path.join(self.game_data_dir, "data", "global", "excel", "cubemain.txt")]
        self._write_page(title=f"Cube Recipes | {self.new_label} Wiki", output_path=WikiRoutes.recipes_index_output_path(), template_name="recipes_index.html", category="index", source_files=cubemain_src, groups=groups, overview=recipe_pages["overview"])
        self._write_page(title=f"Crafting Recipes | {self.new_label} Wiki", output_path=WikiRoutes.recipes_crafting_output_path(), template_name="recipes_crafting.html", category="index", source_files=cubemain_src, page=recipe_pages["crafting"])
        self._write_page(title=f"Corruption Recipes | {self.new_label} Wiki", output_path=WikiRoutes.recipes_corruptions_output_path(), template_name="recipes_corruptions.html", category="index", source_files=cubemain_src, page=recipe_pages["corruptions"])
        self._write_page(title=f"Pierce Recipes | {self.new_label} Wiki", output_path=WikiRoutes.recipes_pierce_output_path(), template_name="recipes_pierce.html", category="index", source_files=cubemain_src, page=recipe_pages["pierce"])
        self._write_page(title=f"Reforge and Upgrade Recipes | {self.new_label} Wiki", output_path=WikiRoutes.recipes_reforge_upgrade_output_path(), template_name="recipes_reforge_upgrade.html", category="index", source_files=cubemain_src, page=recipe_pages["reforge_upgrade"])
        self._write_page(title=f"Rune and Material Recipes | {self.new_label} Wiki", output_path=WikiRoutes.recipes_materials_output_path(), template_name="recipes_materials.html", category="index", source_files=cubemain_src, page=recipe_pages["materials"])
        self._write_page(title=f"All Cube Recipes | {self.new_label} Wiki", output_path=WikiRoutes.recipes_all_output_path(), template_name="recipes_all.html", category="index", source_files=cubemain_src, page=recipe_pages["all"])
        self._write_page(title=f"Raw Cube Recipes | {self.new_label} Wiki", output_path=WikiRoutes.recipes_raw_output_path(), template_name="recipes_raw.html", category="index", source_files=cubemain_src, page=recipe_pages["raw"])

    def _write_bestiary_pages(self, groups: List[MonsterActGroupDTO]) -> None:
        self._write_page(
            title=f"Bestiary | {self.new_label} Wiki",
            output_path=WikiRoutes.bestiary_index_output_path(),
            template_name="bestiary_index.html",
            category="index",
            source_files=[
                os.path.join(self.game_data_dir, "data", "global", "excel", "monstats.txt"),
                os.path.join(self.game_data_dir, "data", "global", "excel", "levels.txt"),
            ],
            groups=groups,
        )

    def _write_misc_pages(self, groups: List[MiscGroupDTO]) -> None:
        ItemIconExporter(self.writer, self.game_data_dir, self.retail_data_dir, repository=self._repo).attach_misc_item_icons(groups)
        self._write_page(
            title=f"Materials | {self.new_label} Wiki",
            output_path=WikiRoutes.misc_index_output_path(),
            template_name="misc_index.html",
            category="index",
            source_files=[os.path.join(self.game_data_dir, "data", "global", "excel", "misc.txt")],
            groups=groups,
        )

    def _write_gems_runes_pages(self, groups: List[MiscGroupDTO], retail_items: Dict[str, Any]) -> None:
        icon_exporter = ItemIconExporter(self.writer, self.game_data_dir, self.retail_data_dir, repository=self._repo)
        icon_exporter.attach_misc_item_icons(groups)

        for group in groups:
            for item in group["members"]:
                old_item = retail_items.get(item["code"])
                item["comparison"] = gem_rune_comparison_context(item, old_item)

        self._write_page(
            title=f"Gems & Runes | {self.new_label} Wiki",
            output_path=WikiRoutes.gems_runes_index_output_path(),
            template_name="gems_runes_index.html",
            category="index",
            source_files=[
                os.path.join(self.game_data_dir, "data", "global", "excel", "misc.txt"),
                os.path.join(self.game_data_dir, "data", "global", "excel", "gems.txt"),
            ],
            groups=groups,
        )

    def _write_mechanics_pages(self, summary: MechanicsSummaryDTO) -> None:
        self._write_page(
            title=f"Mechanics & Progression | {self.new_label} Wiki",
            output_path=WikiRoutes.mechanics_output_path(),
            template_name="mechanics.html",
            category="index",
            source_files=[
                os.path.join(self.game_data_dir, "data", "global", "excel", fname)
                for fname in ("experience.txt", "difficultylevels.txt", "skills.txt", "missiles.txt",
                              "charstats.txt", "properties.txt", "itemstatcost.txt", "gamble.txt")
            ],
            summary=summary,
        )

    def _write_drop_weight_pages(self, groups: List[Dict[str, Any]]) -> None:
        self.writer.write_text("data/drop-weights.json", json.dumps(groups, indent=2))
        self._write_page(
            title=f"Drops | {self.new_label} Wiki",
            output_path=WikiRoutes.drops_index_output_path(),
            template_name="drops_index.html",
            category="index",
            source_files=[
                os.path.join(self.game_data_dir, "data", "global", "excel", fname)
                for fname in ("uniqueitems.txt", "setitems.txt", "treasureclassex.txt")
            ],
            groups=groups,
            set_group_count=sum(1 for g in groups if g["quality"] == "set"),
            unique_group_count=sum(1 for g in groups if g["quality"] == "unique"),
        )

    def _write_drop_source_pages(self, data: Dict[str, Any]) -> None:
        self.writer.write_text("data/drop-sources.json", json.dumps(data, indent=2))
        self._write_page(
            title=f"Drop Sources | {self.new_label} Wiki",
            output_path=WikiRoutes.drop_sources_output_path(),
            template_name="drop_sources.html",
            category="index",
            source_files=[
                os.path.join(self.game_data_dir, "data", "global", "excel", fname)
                for fname in ("treasureclassex.txt", "monstats.txt", "superuniques.txt", "weapons.txt", "armor.txt", "misc.txt")
            ],
            page=data,
            summary=data.get("summary", {}),
            rows=data.get("rows", []),
        )

    def _write_reference_pages(self, pages: List[Dict[str, Any]], coverage: Dict[str, Any]) -> None:
        self.writer.write_text("data/references-raw-coverage.json", json.dumps(coverage, indent=2))
        index_entries = [
            {
                "title": page["title"],
                "description": page["description"],
                "href": WikiRoutes.route_from_output_path(WikiRoutes.reference_output_path(page["slug"])),
                "row_count": page["row_count"],
                "source_tables": page["source_tables"],
                "search_text": page["search_text"],
            }
            for page in pages
            if page["slug"] != AFFIX_FUNCTIONS_SLUG
        ]
        self._write_page(
            title=f"References | {self.new_label} Wiki",
            output_path=WikiRoutes.references_index_output_path(),
            template_name="references_index.html",
            category="index",
            source_files=[],
            pages=index_entries,
            coverage=coverage,
        )

        for page in pages:
            self.writer.write_text(f"data/references-{page['slug']}.json", json.dumps(page, indent=2))
            source_files = [
                os.path.join(self.game_data_dir, "data", "global", "excel", f"{table}.txt")
                for table in page["source_tables"]
            ]
            if page["slug"] == AFFIX_FUNCTIONS_SLUG:
                item_types = {
                    code: label
                    for group in page["sections"]
                    for row in group["rows"]
                    for code, label in row["item_types"].items()
                }
                for slug in ("affixes", AFFIX_FUNCTIONS_SLUG):
                    function_page = dict(page, title="Affixes") if slug == "affixes" else page
                    self._write_page(
                        title=f"{function_page['title']} | {self.new_label} Wiki",
                        output_path=WikiRoutes.reference_output_path(slug),
                        template_name="affix_functions.html",
                        category="index",
                        source_files=source_files,
                        page=function_page,
                        affix_item_types=sorted(item_types.items(), key=lambda item: item[1].casefold()),
                        affix_view="function",
                        affix_default_entry=slug == "affixes",
                    )
                continue
            comparison_sections = [section for section in page["sections"] if "comparison_rows" in section]
            affix_cards = {
                section["table"]: [
                    card
                    for row in section["comparison_rows"]
                    for card in affix_card_contexts(row)
                ]
                for section in comparison_sections
            }
            affix_item_types = {
                code: label
                for section in comparison_sections
                for row in section["comparison_rows"]
                for roll in row["old"] + row["new"]
                for code, label in roll["item_types"].items()
            }
            is_affix_page = page["slug"] == "affixes"
            display_page = dict(page, title="Affix Cards") if is_affix_page else page
            output_slug = "affixes/cards" if is_affix_page else page["slug"]
            self._write_page(
                title=f"{display_page['title']} | {self.new_label} Wiki",
                output_path=WikiRoutes.reference_output_path(output_slug),
                template_name="reference_table.html",
                category="index",
                source_files=source_files,
                page=display_page,
                affix_cards=affix_cards,
                affix_item_types=sorted(affix_item_types.items(), key=lambda item: item[1].casefold()),
                item_section_titles={section["table"]: section["title"] for section in comparison_sections},
                affix_view="cards" if is_affix_page else None,
            )

        coverage_page = {
            "slug": "raw-coverage",
            "title": "Raw Coverage",
            "description": "Every raw Excel txt table detected in the mod data and whether it is mapped into a generated wiki surface.",
            "sections": [
                {
                    "title": "Raw Tables",
                    "table": "coverage",
                    "row_count": len(coverage.get("rows", [])),
                    "rows": [
                        {
                            "label": row["table"],
                            "fields": [
                                {"label": "Rows", "value": str(row["row_count"])},
                                {"label": "Coverage", "value": row["coverage"]},
                                {"label": "Status", "value": row["status"]},
                            ],
                            "properties": [],
                            "search_text": row["search_text"],
                        }
                        for row in coverage.get("rows", [])
                    ],
                }
            ],
        }
        self.writer.write_text("data/references-raw-coverage-page.json", json.dumps(coverage_page, indent=2))
        self._write_page(
            title=f"Raw Coverage | {self.new_label} Wiki",
            output_path=WikiRoutes.reference_output_path("raw-coverage"),
            template_name="reference_table.html",
            category="index",
            source_files=[],
            page=coverage_page,
        )

    def _write_item_pages(
        self,
        items: Dict[str, List[Dict[str, Any]]],
        old_item_index: Dict[str, Dict[str, Dict[str, Any]]],
        base_item_lookup: Dict[str, Any],
        retail_base_items: Dict[str, Any],
    ) -> Dict[str, List[Dict[str, str]]]:
        page_entries: Dict[str, List[Dict[str, str]]] = {family: [] for family in ITEM_FAMILIES}
        icon_exporter = ItemIconExporter(self.writer, self.game_data_dir, self.retail_data_dir, repository=self._repo)
        drop_base_lookup = self._drop_base_lookup(self._repo)
        bk_sets = self._sets_lookup(self._repo)
        retail_sets = self._sets_lookup(self._retail_repo)

        for family, entries in items.items():
            for entry in sorted(entries, key=item_sort_key):
                title = item_title(entry, family)
                identity = item_identity(entry, family)
                old_entry = old_item_index.get(family, {}).get(identity)
                status = item_diff_status(entry, old_entry)
                if family == "set":
                    set_id = str(entry.get("raw_row", {}).get("set") or "").strip()
                    if set_id and not entry.get("set_name"):
                        entry["set_name"] = self._set_display_name(self._repo, bk_sets, set_id)
                    if old_entry and not old_entry.get("set_name"):
                        old_set_id = str(old_entry.get("raw_row", {}).get("set") or "").strip()
                        if old_set_id:
                            old_entry = {**old_entry, "set_name": self._set_display_name(self._retail_repo, retail_sets, old_set_id)}
                    entry["set_anchor"] = set_item_anchor(entry)
                    href = f"sets/#{slugify(set_id)}" if set_id else "sets/"
                else:
                    href = "items/"
                entry["href"] = href

                icon_src = icon_exporter.export_entry_icon(entry, family)
                entry["icon_src"] = icon_src
                if family == "runeword":
                    entry["rune_requirements"] = self._runeword_rune_requirements(entry, icon_exporter)
                entry["drop_info"] = self._item_drop_info(entry, family, drop_base_lookup)
                comparison = item_comparison_context(entry, family, old_entry)
                base_stats = []
                if family in ("unique", "set"):
                    raw_row = entry.get("raw_row", {})
                    base_code = raw_row.get("code" if family == "unique" else "item", "")
                    base_stats = self._base_comparison_rows(base_item_lookup.get(base_code), retail_base_items.get(base_code))
                runes = [
                    {
                        "name": str(rune.get("name", "")).strip(),
                        "code": str(rune.get("code", "")).strip(),
                        "icon_src": str(rune.get("icon_src", "")).strip(),
                    }
                    for rune in entry.get("rune_requirements", [])
                    if str(rune.get("name", "")).strip() or str(rune.get("code", "")).strip()
                ]
                taxonomy = self._taxonomy
                if family == "runeword":
                    categories = sorted({taxonomy.category(base) for base in taxonomy.matching_bases(entry.get("raw_row", {}))})
                else:
                    raw = entry.get("raw_row", {})
                    base = taxonomy.bases.get(raw.get("code") or raw.get("item", ""), {})
                    categories = [taxonomy.category(base)]
                if not categories:
                    categories = [item_filter_type(entry, family)]
                page_entries[family].append({
                    "identity": identity,
                    "title": title,
                    "href": href,
                    "summary": item_summary(entry, family),
                    "search_text": item_search_text(entry, family),
                    "status": status,
                    "history": entry["history"],
                    "item_group": "|".join(sorted({taxonomy.group(category) for category in categories})),
                    "item_type": "|".join(categories),
                    "icon_src": icon_src,
                    "drop_level": entry["drop_info"].get("drop_level", 0),
                    "drop_level_label": entry["drop_info"].get("label", ""),
                    "runes": runes,
                    "properties": [
                        str(prop.get("resolved_text", "")).strip()
                        for prop in entry.get("properties", [])
                        if str(prop.get("resolved_text", "")).strip()
                    ][:5],
                    "base_stats": base_stats,
                    "stat_rows": comparison["stat_rows"],
                    "property_rows": comparison["property_rows"],
                })

        return page_entries

    def _write_class_pages(self, class_pages: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        entries: List[Dict[str, str]] = []
        for page in class_pages:
            title = page["class_name"]
            output_path = WikiRoutes.class_output_path(page.get("class_slug") or slugify(title))
            href = WikiRoutes.route_from_output_path(output_path)
            self._write_page(
                title=f"{title} | Class Skills",
                output_path=output_path,
                template_name="class.html",
                category="class",
                source_files=page["source_files"],
                page=page,
                item_entries={"skill": [skill_card_context(skill) for skill in page["skills"]]},
                item_section_titles={"skill": "Skills"},
            )
            skill_terms = []
            for skill in page["skills"]:
                skill_terms.append(skill["name"])
                if skill.get("id") and skill["id"].casefold() != skill["name"].casefold():
                    skill_terms.append(skill["id"])
            entries.append({
                "title": title,
                "href": href,
                "summary": f"{len(page['skills'])} skills",
                "search_text": f"{title} {' '.join(skill_terms)}",
            })
        return entries

    def _write_runeword_index_page(
        self,
        runewords: List[Dict[str, Any]],
        page_entries: List[Dict[str, str]],
        old_item_index: Optional[Dict] = None,
    ) -> None:
        entry_by_identity = {entry["identity"]: entry for entry in page_entries if entry.get("identity")}
        href_by_title = {entry["title"]: entry for entry in page_entries}
        icon_exporter = ItemIconExporter(self.writer, self.game_data_dir, self.retail_data_dir, repository=self._repo)
        old_runewords = (old_item_index or {}).get("runeword", {})
        records = []
        rune_options_by_code: Dict[str, Dict[str, str]] = {}
        base_options: Dict[str, str] = {}

        for entry in sorted(runewords, key=item_sort_key):
            title = item_title(entry, "runeword")
            identity = item_identity(entry, "runeword")
            page_entry = entry_by_identity.get(identity) or href_by_title.get(title, {})
            rune_requirements = entry.get("rune_requirements") or self._runeword_rune_requirements(entry, icon_exporter)
            base_items = entry.get("base_items", [])
            base_filter_terms = (self._taxonomy.runeword_terms(entry.get("raw_row", {})) or self._runeword_base_filter_terms(base_items))
            for base_term in base_filter_terms:
                base_options[base_term] = base_term

            property_preview = [
                str(prop.get("resolved_text", ""))
                for prop in entry.get("properties", [])
                if str(prop.get("resolved_text", "")).strip()
            ][:5]
            searchable_properties = [
                str(prop.get("resolved_text", ""))
                for prop in entry.get("properties", [])
                if str(prop.get("resolved_text", "")).strip()
            ]

            old_entry = old_runewords.get(item_identity(entry, "runeword"))
            comparison = item_comparison_context(entry, "runeword", old_entry)
            comparison["rune_property_rows"] = self._rune_property_rows(entry, old_entry)
            rune_filter_terms = []
            rune_requirement_codes = []
            for rune in rune_requirements:
                rune_name = str(rune.get("name", "")).strip()
                rune_code = str(rune.get("code", "")).strip()
                short_rune_name = resolve_localized_string(self._repo, f"{rune_code}L") if rune_code else ""
                full_rune_name = resolve_localized_string(self._repo, rune_code) if rune_code else ""
                if not short_rune_name:
                    short_rune_name = rune_name
                rune_terms = []
                for term in (rune_name, full_rune_name, short_rune_name, rune_code):
                    if term and term not in rune_filter_terms:
                        rune_filter_terms.append(term)
                    if term and term not in rune_terms:
                        rune_terms.append(term)
                if rune_code:
                    rune_requirement_codes.append(rune_code)
                    if rune_code not in rune_options_by_code:
                        rune_options_by_code[rune_code] = {
                            "code": rune_code,
                            "name": short_rune_name or rune_name or rune_code,
                            "icon_src": str(rune.get("icon_src", "")),
                            "filter_terms": "|".join(rune_terms),
                        }

            records.append({
                "title": title,
                "href": page_entry.get("href", ""),
                "status": page_entry.get("status", "unchanged"),
                "summary": item_summary(entry, "runeword"),
                "history": entry.get("history"),
                "base_items": base_items,
                "base_filter_terms": "|".join(base_filter_terms),
                "runes": rune_requirements,
                "rune_filter_terms": "|".join(rune_filter_terms),
                "rune_requirement_codes": "|".join(rune_requirement_codes),
                "properties": property_preview,
                "comparison": comparison,
                "search_text": " ".join([
                    title,
                    " ".join(entry.get("base_items", [])),
                    " ".join(rune["name"] for rune in rune_requirements),
                    " ".join(rune["code"] for rune in rune_requirements),
                    " ".join(searchable_properties),
                    page_entry.get("status", ""),
                ]),
            })

        def rune_option_sort(option: Dict[str, str]) -> Tuple[int, str]:
            match = re.search(r"\d+", option.get("code", ""))
            return (int(match.group(0)) if match else 999, option.get("name", ""))

        base_sort_order: Dict[str, int] = {}
        for idx, code in enumerate(("tors", "shld", "mele", "miss", "weap", "helm")):
            lbl = self._taxonomy.label(code)
            if lbl and lbl not in base_sort_order:
                base_sort_order[lbl] = idx

        def base_option_sort(label: str) -> Tuple[int, str]:
            return (base_sort_order.get(label, 20), label)

        self._write_page(
            title=f"Runewords | {self.new_label} Wiki",
            output_path=WikiRoutes.runewords_index_output_path(),
            template_name="runewords_index.html",
            category="index",
            source_files=[os.path.join(self.game_data_dir, "data", "global", "excel", "runes.txt")],
            runewords=records,
            rune_options=sorted(rune_options_by_code.values(), key=rune_option_sort),
            base_options=sorted(base_options.values(), key=base_option_sort),
        )

    @staticmethod
    def _runeword_base_filter_terms(base_items: List[str]) -> List[str]:
        terms: List[str] = []
        for base_item in base_items:
            base_label = str(base_item).strip()
            if base_label and base_label not in terms:
                terms.append(base_label)
        return terms

    @staticmethod
    def _sets_lookup(repo: D2RepositoryProtocol) -> Dict[str, Dict[str, str]]:
        lookup: Dict[str, Dict[str, str]] = {}
        for row in repo.get_excel_table("sets"):
            index_key = str(row.get("index", "")).strip()
            name_key = str(row.get("name", "")).strip()
            if index_key and index_key not in lookup:
                lookup[index_key] = row
            if name_key and name_key not in lookup:
                lookup[name_key] = row
        return lookup

    @staticmethod
    def _set_display_name(repo: D2RepositoryProtocol, sets_lookup: Dict[str, Dict[str, str]], set_id: str) -> str:
        clean_id = str(set_id or "").strip()
        if not clean_id:
            return ""
        set_row = sets_lookup.get(clean_id, {})
        name_key = str(set_row.get("name") or clean_id).strip()
        return resolve_localized_string(repo, name_key) or name_key or clean_id

    def _write_set_index_page(
        self,
        sets: List[Dict[str, Any]],
        old_item_index: Dict[str, Dict[str, Any]],
        base_item_lookup: Dict[str, Any],
        retail_base_items: Dict[str, Any],
    ) -> None:
        set_families: Dict[str, List[Dict[str, Any]]] = {}
        for item in sets:
            set_id = item.get("raw_row", {}).get("set", "Unknown Set")
            set_families.setdefault(set_id, []).append(item)

        prop_groups_path = os.path.join(REPO_ROOT, "data", "propertygroups.txt")
        prop_groups = load_property_groups(self._repo, prop_groups_path)
        retail_prop_groups = load_property_groups(self._retail_repo, prop_groups_path) or prop_groups

        resolver_bk = PropertyResolverService(self._repo, prop_groups)
        resolver_rt = PropertyResolverService(self._retail_repo, retail_prop_groups)

        retail_sets = self._sets_lookup(self._retail_repo)
        bk_sets = self._sets_lookup(self._repo)

        results: List[SetFamilyDTO] = []
        for set_id, members in set_families.items():
            bk_set_row = bk_sets.get(set_id, {})
            rt_set_row = retail_sets.get(set_id, {})
            display_name = self._set_display_name(self._repo, bk_sets, set_id)

            for item in members:
                if not item.get("set_name"):
                    item["set_name"] = display_name
                old_item = old_item_index.get(item_identity(item, "set"))
                if old_item and not old_item.get("set_name"):
                    old_set_id = str(old_item.get("raw_row", {}).get("set") or "").strip()
                    if old_set_id:
                        old_item = {**old_item, "set_name": self._set_display_name(self._retail_repo, retail_sets, old_set_id)}
                item["comparison"] = item_comparison_context(item, "set", old_item)
                item["summary"] = item_summary(item, "set")
                base_code = item.get("raw_row", {}).get("item", "")
                item["base_stats"] = self._base_comparison_rows(
                    base_item_lookup.get(base_code), retail_base_items.get(base_code)
                )

            bonus_diffs = set_bonus_comparison(set_id, bk_set_row, rt_set_row, resolver_bk, resolver_rt)
            status = (
                "added" if not rt_set_row
                else "modified" if any(b["status"] != "same" for b in bonus_diffs) or any(m["comparison"]["state"] == "modified" for m in members)
                else "unchanged"
            )
            search_terms = [display_name]
            if set_id and set_id.casefold() != display_name.casefold():
                search_terms.append(set_id)
            search_terms.extend(m["display_name"] for m in members)
            results.append({
                "id": set_id,
                "anchor": slugify(set_id),
                "name": display_name,
                "summary": f"A {len(members)}-piece set.",
                "set_bonuses": bonus_diffs,
                "members": members,
                "status": status,
                "search_text": " ".join(search_terms),
            })

        results.sort(key=lambda row: (row["name"].casefold(), row["id"].casefold()))

        self._write_page(
            title=f"Set Items | {self.new_label} Wiki",
            output_path=WikiRoutes.sets_index_output_path(),
            template_name="sets_index.html",
            category="index",
            source_files=["data/global/excel/sets.txt", "data/global/excel/setitems.txt"],
            sets=results,
        )

    def _write_indexes(
        self,
        item_entries: Dict[str, List[Dict[str, str]]],
        class_entries: List[Dict[str, str]],
        report_entries: List[Dict[str, str]],
        area_entries: List[Dict[str, Any]],
        base_item_families: List[BaseItemFamilyDTO],
        recipe_groups: List[CubeRecipeGroupDTO],
        monster_groups: List[MonsterActGroupDTO],
        misc_groups: List[MiscGroupDTO],
        gem_rune_groups: List[MiscGroupDTO],
        drop_weight_groups: List[Dict[str, Any]],
        reference_pages: List[Dict[str, Any]],
    ) -> None:
        self._write_page(
            title=f"{self.new_label} Data Wiki",
            output_path=WikiRoutes.home_output_path(),
            template_name="home.html",
            category="index",
            source_files=[],
            item_counts={family: len(item_entries[family]) for family in ITEM_FAMILIES},
            class_count=len(class_entries),
            area_count=len(area_entries),
            base_family_count=len(base_item_families),
            recipe_count=sum(len(g["recipes"]) for g in recipe_groups),
            monster_count=sum(len(g["monsters"]) for g in monster_groups),
            misc_count=sum(len(g["members"]) for g in misc_groups),
            gem_rune_count=sum(len(g["members"]) for g in gem_rune_groups),
            drop_weight_count=len(drop_weight_groups),
            reference_count=sum(page["slug"] != AFFIX_FUNCTIONS_SLUG for page in reference_pages) + 1,
            total_items=sum(len(entries) for entries in item_entries.values()),
            reports=report_entries,
        )

        loot_groups = self._taxonomy.loot_groups()
        group_to_types = {group: set(categories) for group, categories in loot_groups.items()}
        drop_level_breakpoints = sorted({
            int(entry.get("drop_level") or 0)
            for family in ("unique", "set")
            for entry in item_entries[family]
            if 85 < int(entry.get("drop_level") or 0) < 99
        })
        for entries in item_entries.values():
            for entry in entries:
                for group in entry["item_group"].split("|"):
                    if group and group not in group_to_types:
                        group_to_types[group] = set()

        self._write_page(
            title=f"All Items | {self.new_label} Data Wiki",
            output_path=WikiRoutes.items_index_output_path(),
            template_name="items_index.html",
            category="index",
            source_files=[],
            item_entries=item_entries,
            family_counts={family: len(item_entries[family]) for family in ITEM_FAMILIES},
            item_groups=[{"name": g, "types": loot_groups.get(g, sorted(group_to_types[g]))} for g in group_to_types],
            drop_level_breakpoints=drop_level_breakpoints,
        )

        self._write_page(title=f"Classes | {self.new_label} Data Wiki", output_path=WikiRoutes.classes_index_output_path(), template_name="classes_index.html", category="index", source_files=[], classes=class_entries)
        self._write_page(
            title=f"Areas | {self.new_label} Data Wiki",
            output_path=WikiRoutes.areas_index_output_path(),
            template_name="areas_index.html",
            category="index",
            source_files=[
                os.path.join(self.game_data_dir, "data", "global", "excel", "levels.txt"),
                os.path.join(self.game_data_dir, "data", "global", "excel", "monstats.txt"),
                os.path.join(REPO_ROOT, "docs", "Diablo_II_Data_File_Guide", "levels.md"),
            ],
            area_count=len(area_entries),
        )
        self._write_page(title=f"Reports | {self.new_label} Data Wiki", output_path=WikiRoutes.reports_index_output_path(), template_name="reports_index.html", category="index", source_files=[], reports=report_entries)

    def _write_patch_notes_draft(
        self,
        item_entries: Dict[str, List[Dict[str, str]]],
        class_entries: List[Dict[str, str]],
    ) -> None:
        self._write_page(
            title=f"Full Patch Notes Draft | {self.new_label} Data Wiki",
            output_path=WikiRoutes.patch_notes_output_path(),
            template_name="patch_notes.html",
            category="patch",
            source_files=[],
            total_items=sum(len(entries) for entries in item_entries.values()),
            class_count=len(class_entries),
        )

    def _write_item_index_data(self, item_entries: Dict[str, List[Dict[str, str]]], items: Dict[str, List[Dict[str, Any]]]) -> None:
        rows = [
            {
                "title": entry["title"],
                "href": entry["href"],
                "history": entry["history"],
                "family": family,
                "status": entry["status"],
                "item_group": entry["item_group"],
                "item_type": entry["item_type"],
                "icon_src": entry.get("icon_src", ""),
                "summary": entry["summary"],
                "search_text": entry["search_text"],
                "drop_level": entry.get("drop_level", 0),
                "drop_level_label": entry.get("drop_level_label", ""),
                "runes": entry.get("runes", []),
                "properties": entry.get("properties", []),
                "stat_rows": entry.get("stat_rows", []),
                "property_rows": entry.get("property_rows", []),
            }
            for family in ITEM_FAMILIES
            for entry in item_entries[family]
        ]
        for item in rows:
            record = item["history"]
            item["history"] = {"id": record["id"], "coverage": record["coverage"]}
            for event_key in ("first", "last_change"):
                event = record.get(event_key)
                item["history"][event_key] = ({k: event[k] for k in ("kind", "timestamp", "date", "commit", "short_commit", "url", "release")} if event else None)
            for key in ("stat_rows", "property_rows"):
                item[key] = [dict(row,
                    old_html=str(highlight_comparison(row.get("old", ""), row.get("new", ""), "old")),
                    new_html=str(highlight_comparison(row.get("new", ""), row.get("old", ""), "new")),
                ) for row in item[key]]
        self.writer.write_text("data/items-index.json", json.dumps(rows, indent=2))

    def _write_area_index_data(self, area_entries: List[Dict[str, Any]]) -> None:
        self.writer.write_text("data/areas-index.json", json.dumps(area_entries, indent=2))

    def _publish_reports(self) -> List[Dict[str, str]]:
        reports_root = os.path.normpath(os.path.join(self.output_dir, ".."))
        entries: List[Dict[str, str]] = []
        for report in REPORT_SOURCES:
            source_dir = os.path.join(reports_root, report["source_dir"])
            if not os.path.isdir(source_dir):
                continue
            copied_files = 0
            for root, _, files in os.walk(source_dir):
                for filename in files:
                    if not filename.endswith((".html", ".css", ".json")):
                        continue
                    source_path = os.path.join(root, filename)
                    rel_source = os.path.relpath(source_path, source_dir).replace("\\", "/")
                    output_path = f"{report['output_dir']}/{rel_source}"
                    if rel_source == "index.html":
                        groups = ['<p><a href="../../index.html">All reports</a></p>']
                        labels = {"item_diff": "Item differences", "excel_diff": "Raw table differences", "file_diff": "Override file differences"}
                        for suffix, heading in [("retail-bk", "BK vs Retail"), ("bt-bk", "BK vs BT")]:
                            links = []
                            for other in REPORT_SOURCES:
                                if not other["output_dir"].endswith(suffix) or not os.path.isfile(os.path.join(reports_root, other["source_dir"], "index.html")):
                                    continue
                                label = labels[other["source_kind"]]
                                if other == report:
                                    links.append(f'<li><strong aria-current="page">{label} (current)</strong></li>')
                                else:
                                    target = os.path.relpath(f"{other['output_dir']}/index.html", report["output_dir"]).replace("\\", "/")
                                    links.append(f'<li><a href="{html.escape(target, quote=True)}">{label}</a></li>')
                            if links:
                                groups.append(f'<section><h2>{heading}</h2><ul>' + "".join(links) + '</ul></section>')
                        navigation = '<nav aria-label="Report summaries">' + groups[0] + '<div style="display:flex;flex-wrap:wrap;gap:16px 48px">' + "".join(groups[1:]) + '</div></nav>'
                        with open(source_path, encoding="utf-8") as source:
                            content = source.read()
                        content = re.sub(r'(<main\b[^>]*>)', lambda match: match.group(1) + navigation, content, count=1)
                        self.writer.write_text(output_path, content)
                    else:
                        self.writer.copy_asset(source_path, output_path)
                    copied_files += 1
            if copied_files == 0:
                continue
            href = WikiRoutes.route_from_output_path(f"{report['output_dir']}/index.html")
            entries.append({
                "title": report["title"],
                "href": href,
                "summary": report["description"],
                "source_dir": report["source_dir"],
                "source_kind": report["source_kind"],
                "comparison": "BK vs Retail" if report["output_dir"].endswith("retail-bk") else "BK vs BT",
                "file_count": str(copied_files),
            })
            self.manifest.append({"title": report["title"], "path": href, "category": "report", "sources": [report["source_dir"]]})
        return entries

    def _write_manifest(self) -> None:
        self.writer.write_text("manifest.json", json.dumps(self.manifest, indent=2))

    def _write_page(self, title: str, output_path: str, template_name: str, category: str, source_files: List[str], **context: Any) -> None:
        normalized = output_path.replace("\\", "/")
        self.site["pages"].append({
            "kind": os.path.splitext(template_name)[0],
            "title": title,
            "output_path": normalized,
            "template_name": template_name,
            "category": category,
            "source_files": source_files,
            "payload": context,
        })
        self.writer.generated_paths.add(normalized)
        self.manifest.append({"title": title, "path": WikiRoutes.route_from_output_path(output_path), "category": category, "sources": source_files})

    # ── Item page context (needs instance state) ─────────────────────────────

    def _base_comparison_rows(
        self,
        bk_base: Dict[str, Any],
        retail_base: Optional[Dict[str, Any]],
    ) -> List[Dict[str, str]]:
        labels = {
            "Def": "Def",
            "One-Hand Damage": "One-Hand Damage",
            "Two-Hand Damage": "Two-Hand Damage",
            "Throwing Damage": "Throw Damage",
            "Max Sockets": "Max Sockets",
        }
        comparison = base_item_comparison_context(bk_base or {}, retail_base or {})
        return [
            {**row, "label": labels[row["label"]]}
            for row in comparison["stat_rows"]
            if row["label"] in labels
        ]

    def _rune_property_rows(
        self,
        entry: Dict[str, Any],
        old_entry: Optional[Dict[str, Any]],
    ) -> List[Dict[str, str]]:
        old_rune = rune_property_occurrence_map(old_entry or {})
        new_rune = rune_property_occurrence_map(entry)

        def status(old_v: str, new_v: str) -> str:
            if old_v and new_v:
                return "changed" if old_v != new_v else "same"
            return "added" if new_v else "removed" if old_v else "same"

        keys = list(new_rune.keys()) + [k for k in old_rune if k not in new_rune]
        return [
            {"old": old_rune.get(k, ""), "new": new_rune.get(k, ""),
             "status": status(old_rune.get(k, ""), new_rune.get(k, ""))}
            for k in keys
        ]

    @staticmethod
    def _runeword_rune_name(entry: Dict[str, Any], rune_index: int) -> str:
        runes = entry.get("runes", [])
        return str(runes[rune_index]) if rune_index < len(runes) else ""

    def _runeword_rune_requirements(
        self,
        entry: Dict[str, Any],
        icon_exporter: ItemIconExporter,
    ) -> List[Dict[str, str]]:
        requirements = []
        raw_row = entry.get("raw_row", {})
        for index in range(1, 7):
            rune_code = str(raw_row.get(f"Rune{index}", "")).strip()
            if not rune_code or rune_code == "xxx":
                continue
            rune_name = self._runeword_rune_name(entry, len(requirements))
            requirements.append({
                "code": rune_code,
                "name": rune_name or rune_code,
                "icon_src": icon_exporter.export_icon(output_key=f"rune-{rune_code}", item_code=rune_code, icon_key=rune_code),
            })

        if requirements:
            return requirements

        return [{"code": "", "name": str(rune_name), "icon_src": ""} for rune_name in entry.get("runes", [])]

    # ── Drop weight helpers ───────────────────────────────────────────────────

    @staticmethod
    def _drop_base_name_lookup(repo: D2RepositoryProtocol) -> Dict[str, str]:
        base_names: Dict[str, str] = {}
        for table_name in ("weapons", "armor", "misc"):
            for row in repo.get_excel_table(table_name):
                code = str(row.get("code", "")).strip()
                if not code:
                    continue
                namestr = str(row.get("namestr") or "").strip()
                raw_name = str(row.get("name") or "").strip()
                base_names[code] = (
                    resolve_localized_string(repo, namestr)
                    or resolve_localized_string(repo, raw_name)
                    or raw_name
                    or namestr
                    or code
                )
        return base_names

    @staticmethod
    def _quality_drop_weight_groups(
        rows: List[Dict[str, str]],
        quality: str,
        code_column: str,
        base_names: Dict[str, str],
        repo: Optional[D2RepositoryProtocol] = None,
    ) -> List[Dict[str, Any]]:
        grouped: Dict[str, List[Dict[str, Any]]] = {}
        for row in rows:
            if str(row.get("disabled", "")).strip() in {"1", "true", "TRUE"}:
                continue
            if str(row.get("spawnable", "1")).strip() == "0":
                continue
            code = str(row.get(code_column, "")).strip()
            if not code:
                continue
            try:
                weight = int(str(row.get("rarity", "") or "0"))
            except ValueError:
                weight = 0
            if weight <= 0:
                continue
            raw_id = str(row.get("index") or "").strip()
            fallback_name = raw_id or str(row.get("*ItemName") or code).strip()
            display_name = (
                (resolve_localized_string(repo, raw_id) if repo is not None and raw_id else "")
                or fallback_name
            )
            grouped.setdefault(code, []).append({
                "id": raw_id or code,
                "name": display_name,
                "weight": weight,
                "level": str(row.get("lvl", "")).strip(),
                "level_req": str(row.get("lvl req", "")).strip(),
            })

        result: List[Dict[str, Any]] = []
        for code, candidates in grouped.items():
            if len(candidates) < 2:
                continue
            total_weight = sum(c["weight"] for c in candidates)
            if total_weight <= 0:
                continue
            enriched = [
                {**c, "chance": c["weight"] / total_weight * 100, "chance_display": f"{c['weight'] / total_weight * 100:.1f}%"}
                for c in sorted(candidates, key=lambda r: (-r["weight"], r["name"].lower()))
            ]
            candidate_terms: List[str] = []
            for candidate in enriched:
                candidate_terms.append(candidate["name"])
                if candidate["id"] and candidate["id"].casefold() != candidate["name"].casefold():
                    candidate_terms.append(candidate["id"])
            result.append({
                "id": f"{quality}-{slugify(code)}",
                "quality": quality,
                "quality_label": quality.title(),
                "base_code": code,
                "base_name": base_names.get(code, code),
                "candidate_count": len(enriched),
                "total_weight": total_weight,
                "max_chance": max(c["chance"] for c in enriched),
                "candidates": enriched,
                "search_text": " ".join([quality, code, base_names.get(code, code), *candidate_terms]),
            })
        return result

    @staticmethod
    def _drop_base_lookup(repo: D2Repository) -> Dict[str, Dict[str, Any]]:
        lookup: Dict[str, Dict[str, Any]] = {}

        def to_int(value: Any) -> int:
            try:
                return int(str(value).strip() or "0")
            except ValueError:
                return 0

        for table_name in ("weapons", "armor", "misc"):
            for row in repo.get_excel_table(table_name):
                code = str(row.get("code", "")).strip()
                if not code:
                    continue
                name_key = str(row.get("namestr") or row.get("name") or code).strip()
                display_name = repo.get_string(name_key) or str(row.get("name") or name_key or code).strip()
                lookup[code] = {"code": code, "name": display_name, "level": to_int(row.get("level")), "source_table": f"{table_name}.txt"}
        return lookup

    @staticmethod
    def _item_drop_info(entry: Dict[str, Any], family: str, base_lookup: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        if family not in {"unique", "set"}:
            return {}
        raw_row = entry.get("raw_row", {}) or {}
        base_code_column = "code" if family == "unique" else "item"
        base_code = str(raw_row.get(base_code_column, "")).strip()
        base_info = base_lookup.get(base_code, {})

        def to_int(value: Any) -> int:
            try:
                return int(str(value).strip() or "0")
            except ValueError:
                return 0

        item_level = to_int(raw_row.get("lvl"))
        base_level = to_int(base_info.get("level"))
        drop_level = max(item_level, base_level)
        if drop_level <= 0:
            return {}

        parts = []
        if item_level:
            parts.append(f"item {item_level}")
        if base_level:
            parts.append(f"base {base_level}")
        detail = f" ({', '.join(parts)})" if parts else ""
        return {
            "drop_level": drop_level,
            "label": f"{drop_level}+{detail}",
            "item_level": item_level,
            "base_level": base_level,
            "base_code": base_code,
            "base_name": base_info.get("name", ""),
        }



class WikiGenerator:
    """Compatibility facade for generating the HTML wiki from the shared site DTO."""

    def __init__(
        self,
        item_db_dir: str,
        skill_tree_dir: str,
        output_dir: str,
        old_item_db_dir: Optional[str] = None,
        old_label: str = "Retail",
        new_label: str = "BKDiablo",
        game_data_dir: Optional[str] = None,
        retail_data_dir: Optional[str] = None,
        layout_data_dir: Optional[str] = None,
        locale: str = "enUS",
    ):
        self.item_db_dir = item_db_dir
        self.skill_tree_dir = skill_tree_dir
        self.output_dir = output_dir
        self.old_item_db_dir = old_item_db_dir
        self.old_label = old_label
        self.new_label = new_label
        self.game_data_dir = game_data_dir
        self.retail_data_dir = retail_data_dir
        self.layout_data_dir = layout_data_dir
        self.locale = locale

    def build_site(self) -> WikiSiteDTO:
        return WikiContentBuilder(
            self.item_db_dir,
            self.skill_tree_dir,
            self.output_dir,
            old_item_db_dir=self.old_item_db_dir,
            old_label=self.old_label,
            new_label=self.new_label,
            game_data_dir=self.game_data_dir,
            retail_data_dir=self.retail_data_dir,
            layout_data_dir=self.layout_data_dir,
            locale=self.locale,
        ).build()

    def generate(self) -> WikiSiteDTO:
        site = self.build_site()
        WikiPublisher(self.output_dir).publish(site, HtmlWikiRenderer())
        return site
