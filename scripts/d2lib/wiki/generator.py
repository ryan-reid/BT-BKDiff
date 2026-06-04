from __future__ import annotations
import json
import os
import re
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlencode

from d2lib.repository import D2Repository
from d2lib.services import (
    PropertyResolverService,
    BaseItemAnalyzerService,
    CubeAnalyzerService,
    MonsterAnalyzerService,
    MiscAnalyzerService,
    MechanicsAnalyzerService,
)
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
from d2lib.utils import slugify, strip_markdown
from d2lib.wiki.routes import ITEM_FAMILIES, REPORT_SOURCES, WikiRoutes
from d2lib.wiki.renderers import WikiRenderer, WikiOutputWriter
from d2lib.wiki.builders import AreaFarmingDataBuilder, ItemIconExporter
from d2lib.wiki.comparison import (
    item_diff_status,
    property_occurrence_map,
    rune_property_occurrence_map,
    item_comparison_context,
    base_item_comparison_context,
    gem_rune_comparison_context,
    set_bonus_comparison,
    align_set_member_comparisons,
    comparison_summary_context,
    runeword_compare_rows,
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
    item_slug,
    set_item_anchor,
)

MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
D2LIB_DIR = os.path.dirname(MODULE_DIR)
REPO_ROOT = os.path.abspath(os.path.join(D2LIB_DIR, "..", ".."))


class WikiGenerator:
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
        self.renderer = WikiRenderer()
        self.writer = WikiOutputWriter(output_dir)
        self.manifest: List[Dict[str, Any]] = []
        self._repo: Optional[D2Repository] = None
        self._retail_repo: Optional[D2Repository] = None

    def generate(self) -> None:
        os.makedirs(self.output_dir, exist_ok=True)
        self.manifest = []
        self.writer.generated_paths = set()

        # Cached repos — all _load_* and _write_* methods share these instances.
        self._repo = D2Repository(self.game_data_dir)
        self._retail_repo = D2Repository(self.retail_data_dir)

        items = self._load_items()
        old_items = (
            self._load_items(self.old_item_db_dir)
            if self.old_item_db_dir
            else {family: [] for family in ITEM_FAMILIES}
        )
        old_item_index = self._index_items(old_items)
        class_pages = self._load_class_pages()
        area_entries = self._load_area_entries()
        base_item_families = self._load_base_item_families()
        retail_base_items = self._load_retail_base_items()

        # Single CubeAnalyzerService for both group summary and raw recipes.
        recipe_service = CubeAnalyzerService(self._repo, self._retail_repo)
        recipe_groups = recipe_service.analyze_all_recipes()
        raw_recipes = recipe_service.analyze_raw_recipes(include_removed=True)
        recipe_pages_data = RecipePresentationBuilder(recipe_service, raw_recipes, recipe_groups).build()

        monster_groups = self._load_monster_groups()
        misc_groups, gem_rune_groups = self._load_misc_groups()
        retail_misc_items = self._load_retail_misc_items()
        mechanics_summary = self._load_mechanics_summary()
        drop_weight_groups = self._load_drop_weight_groups()

        self._write_assets()
        item_entries = self._write_item_pages(items, old_item_index)
        class_entries = self._write_class_pages(class_pages)
        self._write_runeword_index_page(items["runeword"], item_entries["runeword"], old_item_index)
        self._write_set_index_page(items["set"], old_item_index["set"])
        self._write_base_item_pages(base_item_families, retail_base_items)
        self._write_recipe_pages(recipe_groups, recipe_pages_data)
        self._write_bestiary_pages(monster_groups)
        self._write_misc_pages(misc_groups)
        self._write_gems_runes_pages(gem_rune_groups, retail_misc_items)
        self._write_mechanics_pages(mechanics_summary)
        self._write_drop_weight_pages(drop_weight_groups)
        report_entries = self._publish_reports()
        self._write_indexes(item_entries, class_entries, report_entries, area_entries, base_item_families, recipe_groups, monster_groups, misc_groups, gem_rune_groups, drop_weight_groups)
        self._write_patch_notes_draft(item_entries, class_entries)
        self._write_item_index_data(item_entries, items)
        self._write_area_index_data(area_entries)
        self._write_manifest()
        self.writer.remove_stale_files()

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
        gem_rune_categories = {"Runes", "Gems & Skulls"}
        gem_rune_groups = [g for g in groups if g["category"] in gem_rune_categories]
        material_groups = [g for g in groups if g["category"] not in gem_rune_categories]
        return material_groups, gem_rune_groups

    def _load_mechanics_summary(self) -> MechanicsSummaryDTO:
        return MechanicsAnalyzerService(self._repo, self._retail_repo).analyze_mechanics()

    def _load_drop_weight_groups(self) -> List[Dict[str, Any]]:
        base_names = self._drop_base_name_lookup(self._repo)
        groups: List[Dict[str, Any]] = []
        groups.extend(self._quality_drop_weight_groups(self._repo.get_excel_table("setitems"), "set", "item", base_names))
        groups.extend(self._quality_drop_weight_groups(self._repo.get_excel_table("uniqueitems"), "unique", "code", base_names))
        return sorted(groups, key=lambda row: (row["base_name"].lower(), row["quality"], -row["max_chance"]))

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
        pages: List[Dict[str, Any]] = []
        if not os.path.isdir(self.skill_tree_dir):
            return pages
        for filename in sorted(os.listdir(self.skill_tree_dir)):
            if not filename.endswith("_skills.md"):
                continue
            full_path = os.path.join(self.skill_tree_dir, filename)
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
            heading = content.splitlines()[0].lstrip("# ").strip() if content else filename
            class_name = heading.replace(" Skill Tree", "").strip()
            pages.append({
                "class_name": class_name,
                "skills": self._parse_skill_tree_markdown(content),
                "source_path": full_path,
            })
        return pages

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
        icon_exporter = ItemIconExporter(self.writer, self.game_data_dir, self.retail_data_dir)
        icon_exporter.attach_base_item_icons(families)

        for family in families:
            for item in family["members"]:
                old_item = retail_items.get(item["code"])
                item["comparison"] = base_item_comparison_context(item, old_item)
                item["href"] = ""

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
            base_groups=sorted({family["group"] for family in families}),
            base_classes=sorted({cn for family in families for cn in family["class_tags"]}),
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
        ItemIconExporter(self.writer, self.game_data_dir, self.retail_data_dir).attach_misc_item_icons(groups)
        self._write_page(
            title=f"Materials | {self.new_label} Wiki",
            output_path=WikiRoutes.misc_index_output_path(),
            template_name="misc_index.html",
            category="index",
            source_files=[os.path.join(self.game_data_dir, "data", "global", "excel", "misc.txt")],
            groups=groups,
        )

    def _write_gems_runes_pages(self, groups: List[MiscGroupDTO], retail_items: Dict[str, Any]) -> None:
        icon_exporter = ItemIconExporter(self.writer, self.game_data_dir, self.retail_data_dir)
        icon_exporter.attach_misc_item_icons(groups)

        for group in groups:
            for item in group["members"]:
                slug = slugify(item["name"])
                output_path = WikiRoutes.gem_rune_output_path(slug)
                item["href"] = WikiRoutes.route_from_output_path(output_path)

                old_item = retail_items.get(item["code"])
                comparison = gem_rune_comparison_context(item, old_item)
                item["comparison"] = comparison

                stats = [
                    {"label": "Code", "value": item["code"]},
                    {"label": "Level", "value": str(item["level"])},
                    {"label": "Level Requirement", "value": str(item["level_req"])},
                ]
                if item["stackable"]:
                    stats.append({"label": "Max Stack", "value": str(item["max_stack"])})

                self._write_page(
                    title=f"{item['name']} | Gems & Runes",
                    output_path=output_path,
                    template_name="item.html",
                    category="gem-rune",
                    source_files=["data/global/excel/misc.txt"],
                    page={
                        "family": "misc",
                        "title": item["name"],
                        "hero_eyebrow": f"{group['category']} Item",
                        "summary": item["description"] or f"A {group['category'].lower()} used for socketing or crafting.",
                        "chips": [
                            {"label": group["category"], "tone": "default"},
                            {"label": self.new_label, "tone": "accent"},
                        ],
                        "stats": stats,
                        "icon_src": item["icon_src"],
                        "source_rel_path": f"misc.txt ({item['code']})",
                        "comparison": comparison,
                    },
                )

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

    def _write_item_pages(
        self,
        items: Dict[str, List[Dict[str, Any]]],
        old_item_index: Dict[str, Dict[str, Dict[str, Any]]],
    ) -> Dict[str, List[Dict[str, str]]]:
        page_entries: Dict[str, List[Dict[str, str]]] = {family: [] for family in ITEM_FAMILIES}
        used_paths: Dict[str, Dict[str, int]] = {family: {} for family in ITEM_FAMILIES}
        icon_exporter = ItemIconExporter(self.writer, self.game_data_dir, self.retail_data_dir)
        drop_base_lookup = self._drop_base_lookup(self._repo)

        for family, entries in items.items():
            for entry in sorted(entries, key=item_sort_key):
                title = item_title(entry, family)
                old_entry = old_item_index.get(family, {}).get(item_identity(entry, family))
                status = item_diff_status(entry, old_entry)
                if family == "set":
                    set_name = str(entry.get("raw_row", {}).get("set") or "").strip()
                    entry["set_anchor"] = set_item_anchor(entry)
                    href = f"sets/#{slugify(set_name)}" if set_name else "sets/"
                    output_path = ""
                else:
                    slug = item_slug(entry, family, title, used_paths[family])
                    output_path = WikiRoutes.item_output_path(family, slug)
                    href = WikiRoutes.route_from_output_path(output_path)
                entry["href"] = href

                icon_src = icon_exporter.export_entry_icon(entry, family)
                entry["icon_src"] = icon_src
                if family == "runeword":
                    entry["rune_requirements"] = self._runeword_rune_requirements(entry, icon_exporter)
                entry["drop_info"] = self._item_drop_info(entry, family, drop_base_lookup)
                comparison = item_comparison_context(entry, family, old_entry)
                page_entries[family].append({
                    "title": title,
                    "href": href,
                    "summary": item_summary(entry, family),
                    "search_text": item_search_text(entry, family),
                    "status": status,
                    "item_group": item_filter_group(entry, family),
                    "item_type": item_filter_type(entry, family),
                    "icon_src": icon_src,
                    "drop_level": entry["drop_info"].get("drop_level", 0),
                    "drop_level_label": entry["drop_info"].get("label", ""),
                    "properties": [
                        str(prop.get("resolved_text", "")).strip()
                        for prop in entry.get("properties", [])
                        if str(prop.get("resolved_text", "")).strip()
                    ][:5],
                    "stat_rows": comparison["stat_rows"],
                    "property_rows": comparison["property_rows"],
                })

                if output_path:
                    self._write_page(
                        title=f"{title} | {family.title()} Item",
                        output_path=output_path,
                        template_name="item.html",
                        category=family,
                        source_files=[entry["_source_rel_path"]],
                        page=self._item_page_context(entry, family, title, old_entry),
                    )

        return page_entries

    def _write_class_pages(self, class_pages: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        entries: List[Dict[str, str]] = []
        for page in class_pages:
            title = page["class_name"]
            output_path = WikiRoutes.class_output_path(slugify(title))
            href = WikiRoutes.route_from_output_path(output_path)
            self._write_page(
                title=f"{title} | Class Skills",
                output_path=output_path,
                template_name="class.html",
                category="class",
                source_files=[page["source_path"]],
                page=page,
            )
            entries.append({
                "title": title,
                "href": href,
                "summary": f"{len(page['skills'])} generated skill entries",
                "search_text": f"{title} {' '.join(skill['name'] for skill in page['skills'])}",
            })
        return entries

    def _write_runeword_index_page(
        self,
        runewords: List[Dict[str, Any]],
        page_entries: List[Dict[str, str]],
        old_item_index: Optional[Dict] = None,
    ) -> None:
        href_by_title = {entry["title"]: entry for entry in page_entries}
        icon_exporter = ItemIconExporter(self.writer, self.game_data_dir, self.retail_data_dir)
        old_runewords = (old_item_index or {}).get("runeword", {})
        records = []

        for entry in sorted(runewords, key=item_sort_key):
            title = item_title(entry, "runeword")
            page_entry = href_by_title.get(title, {})
            rune_requirements = entry.get("rune_requirements") or self._runeword_rune_requirements(entry, icon_exporter)

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

            records.append({
                "title": title,
                "href": page_entry.get("href", ""),
                "status": page_entry.get("status", "unchanged"),
                "summary": item_summary(entry, "runeword"),
                "base_items": entry.get("base_items", []),
                "runes": rune_requirements,
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

        self._write_page(
            title=f"Runewords | {self.new_label} Wiki",
            output_path=WikiRoutes.runewords_index_output_path(),
            template_name="runewords_index.html",
            category="index",
            source_files=[os.path.join(self.game_data_dir, "data", "global", "excel", "runes.txt")],
            runewords=records,
        )

    def _write_set_index_page(self, sets: List[Dict[str, Any]], old_item_index: Dict[str, Dict[str, Any]]) -> None:
        set_families: Dict[str, List[Dict[str, Any]]] = {}
        for item in sets:
            set_name = item.get("raw_row", {}).get("set", "Unknown Set")
            set_families.setdefault(set_name, []).append(item)

        prop_groups_path = os.path.join(REPO_ROOT, "BT-BKDiff", "data", "propertygroups.txt")
        prop_groups = self._repo.load_tsv(prop_groups_path)

        resolver_bk = PropertyResolverService(self._repo, prop_groups)
        resolver_rt = PropertyResolverService(self._retail_repo, prop_groups)

        retail_sets = {row["name"]: row for row in self._retail_repo.get_excel_table("sets")}
        bk_sets = {row["name"]: row for row in self._repo.get_excel_table("sets")}

        results: List[SetFamilyDTO] = []
        for name, members in sorted(set_families.items()):
            bk_set_row = bk_sets.get(name, {})
            rt_set_row = retail_sets.get(name, {})

            for item in members:
                old_item = old_item_index.get(item_identity(item, "set"))
                item["comparison"] = item_comparison_context(item, "set", old_item)
            align_set_member_comparisons(members)

            bonus_diffs = set_bonus_comparison(name, bk_set_row, rt_set_row, resolver_bk, resolver_rt)
            status = (
                "added" if not rt_set_row
                else "modified" if any(b["status"] != "same" for b in bonus_diffs) or any(m["comparison"]["state"] == "modified" for m in members)
                else "unchanged"
            )
            results.append({
                "name": name,
                "summary": f"A {len(members)}-piece set.",
                "set_bonuses": bonus_diffs,
                "members": members,
                "status": status,
                "search_text": f"{name} " + " ".join(m["display_name"] for m in members),
            })

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
            total_items=sum(len(entries) for entries in item_entries.values()),
            reports=report_entries,
        )

        group_to_types: Dict[str, set] = {}
        drop_level_breakpoints = sorted({
            int(entry.get("drop_level") or 0)
            for family in ("unique", "set")
            for entry in item_entries[family]
            if 85 < int(entry.get("drop_level") or 0) < 99
        })
        for entries in item_entries.values():
            for entry in entries:
                group_to_types.setdefault(entry["item_group"], set()).add(entry["item_type"])

        self._write_page(
            title=f"All Items | {self.new_label} Data Wiki",
            output_path=WikiRoutes.items_index_output_path(),
            template_name="items_index.html",
            category="index",
            source_files=[],
            family_counts={family: len(item_entries[family]) for family in ITEM_FAMILIES},
            item_groups=[{"name": g, "types": sorted(group_to_types[g])} for g in sorted(group_to_types)],
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
                "family": family,
                "status": entry["status"],
                "item_group": entry["item_group"],
                "item_type": entry["item_type"],
                "icon_src": entry.get("icon_src", ""),
                "summary": entry["summary"],
                "search_text": entry["search_text"],
                "drop_level": entry.get("drop_level", 0),
                "drop_level_label": entry.get("drop_level_label", ""),
                "properties": entry.get("properties", []),
                "stat_rows": entry.get("stat_rows", []),
                "property_rows": entry.get("property_rows", []),
            }
            for family in ("unique", "set")
            for entry in item_entries[family]
        ]
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
                    self.writer.copy_asset(source_path, f"{report['output_dir']}/{rel_source}")
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
                "file_count": str(copied_files),
            })
            self.manifest.append({"title": report["title"], "path": href, "category": "report", "sources": [report["source_dir"]]})
        return entries

    def _write_manifest(self) -> None:
        self.writer.write_text("manifest.json", json.dumps(self.manifest, indent=2))

    def _write_page(self, title: str, output_path: str, template_name: str, category: str, source_files: List[str], **context: Any) -> None:
        document = self.renderer.render(
            template_name,
            title=title,
            site_root=WikiRoutes.site_root_for_output_path(output_path),
            old_label=self.old_label,
            new_label=self.new_label,
            **context,
        )
        self.writer.write_text(output_path, document)
        self.manifest.append({"title": title, "path": WikiRoutes.route_from_output_path(output_path), "category": category, "sources": source_files})

    # ── Item page context (needs instance state) ─────────────────────────────

    def _item_page_context(
        self,
        entry: Dict[str, Any],
        family: str,
        title: str,
        old_entry: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        chips = [{"label": family.title(), "tone": "default"}, {"label": self.new_label, "tone": "accent"}]
        hero_eyebrow = "Generated Item Page"
        if family == "runeword":
            rune_requirements = entry.get("rune_requirements", [])
            socket_count = len(rune_requirements) or len(entry.get("runes", []))
            base_items = entry.get("base_items", [])
            base_label = ", ".join(base_items) or "Unknown base"
            hero_eyebrow = f"{base_label} Runeword"
            chips = [
                {"label": "Runeword", "tone": "default"},
                {"label": self.new_label, "tone": "accent"},
                {"label": base_label, "tone": "default"},
                {"label": f"{socket_count} socket{'s' if socket_count != 1 else ''}", "tone": "accent"},
            ]
            stats = [
                {"label": "Base", "value": base_label},
                {"label": "Sockets", "value": str(socket_count) if socket_count else "Unknown"},
                {"label": "Runes", "value": " + ".join(entry.get("runes", [])) or "Unknown"},
            ]
        else:
            chips.append({"label": "Set Item" if family == "set" else entry.get("item_type", "Item"), "tone": "accent"})
            stats = [
                {"label": "Base Item", "value": entry.get("base_item", "Unknown")},
                {"label": "Item Type", "value": entry.get("item_type", "Unknown")},
                {"label": "Level Requirement", "value": entry.get("lvl_req", "0")},
            ]
            drop_info = entry.get("drop_info") or {}
            if drop_info.get("label"):
                stats.append({"label": "Drop Level", "value": drop_info["label"]})
            if family == "set" and entry.get("raw_row", {}).get("set"):
                set_name = str(entry["raw_row"]["set"])
                stats.append({"label": "Set", "value": set_name, "href": f"sets/#{slugify(set_name)}"})

        properties = [
            {"text": str(prop.get("resolved_text", "")), "is_warning": "unknown property:" in str(prop.get("resolved_text", "")).lower()}
            for prop in entry.get("properties", [])
        ]
        rune_properties = [
            {
                "rune": str(rune_entry.get("rune", "")),
                "properties": [
                    {"text": str(prop.get("resolved_text", "")), "is_warning": "unknown property:" in str(prop.get("resolved_text", "")).lower()}
                    for prop in rune_entry.get("properties", [])
                ],
            }
            for rune_entry in entry.get("rune_properties", [])
        ]
        comparison = item_comparison_context(entry, family, old_entry)
        return {
            "family": family,
            "title": title,
            "hero_eyebrow": hero_eyebrow,
            "summary": item_summary(entry, family),
            "chips": chips,
            "stats": stats,
            "properties": properties,
            "rune_properties": rune_properties,
            "rune_requirements": entry.get("rune_requirements", []),
            "base_filter_url": self._runeword_base_filter_url(entry, len(entry.get("rune_requirements", []))),
            "old_base_label": ", ".join(old_entry.get("base_items", [])) if old_entry else "",
            "old_rune_label": " + ".join(old_entry.get("runes", [])) if old_entry else "",
            "required_level": entry.get("required_level", ""),
            "runeword_compare_rows": runeword_compare_rows(entry, old_entry),
            "icon_src": entry.get("icon_src", ""),
            "source_rel_path": entry.get("_source_rel_path", ""),
            "comparison": comparison,
            "comparison_summary": comparison_summary_context(comparison),
        }

    @staticmethod
    def _runeword_base_filter_url(entry: Dict[str, Any], socket_count: int) -> str:
        if not entry.get("base_items") and not socket_count:
            return "bases/"
        params: Dict[str, str] = {}
        base_items = [str(base).strip() for base in entry.get("base_items", []) if str(base).strip()]
        if base_items:
            params["category"] = base_items[0]
        if socket_count:
            params["minSockets"] = str(socket_count)
        return f"bases/?{urlencode(params)}" if params else "bases/"

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
    def _drop_base_name_lookup(repo: D2Repository) -> Dict[str, str]:
        base_names: Dict[str, str] = {}
        for table_name in ("weapons", "armor", "misc"):
            for row in repo.get_excel_table(table_name):
                code = str(row.get("code", "")).strip()
                if not code:
                    continue
                name = str(row.get("name") or row.get("namestr") or code).strip()
                base_names[code] = repo.get_string(name) if name else code
        return base_names

    @staticmethod
    def _quality_drop_weight_groups(
        rows: List[Dict[str, str]],
        quality: str,
        code_column: str,
        base_names: Dict[str, str],
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
            grouped.setdefault(code, []).append({
                "name": str(row.get("index") or row.get("*ItemName") or code).strip(),
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
                "search_text": " ".join([quality, code, base_names.get(code, code)] + [c["name"] for c in enriched]),
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

    # ── Skill tree parsing ───────────────────────────────────────────────────

    def _parse_skill_tree_markdown(self, content: str) -> List[Dict[str, Any]]:
        lines = content.splitlines()
        skills: List[Dict[str, Any]] = []
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if not line.startswith("## "):
                i += 1
                continue

            skill_name = line[3:].strip()
            i += 1
            wip = False
            table_rows: List[Dict[str, str]] = []
            synergies: List[Dict[str, str]] = []

            while i < len(lines):
                stripped = lines[i].strip()
                if stripped.startswith("## "):
                    break
                if stripped == "> Work in Progress":
                    wip = True
                    i += 1
                    continue
                if stripped.startswith("| Effect |"):
                    i += 2
                    while i < len(lines):
                        row_line = lines[i].strip()
                        if not row_line.startswith("|"):
                            break
                        parts = [p.strip() for p in row_line.strip("|").split("|")]
                        if len(parts) >= 7:
                            table_rows.append({
                                "effect": strip_markdown(parts[0]),
                                "scaling": strip_markdown(parts[1]),
                                "l1": strip_markdown(parts[2]),
                                "l10": strip_markdown(parts[3]),
                                "l20": strip_markdown(parts[4]),
                                "l20_soft10": strip_markdown(parts[5]),
                                "limit": strip_markdown(parts[6]),
                            })
                        i += 1
                    continue
                if stripped == "### Synergies":
                    i += 1
                    while i < len(lines):
                        syn_line = lines[i].strip()
                        if not syn_line.startswith("* "):
                            break
                        match = re.match(r"\* \*\*(.+?)\*\*: (.+)", syn_line)
                        if match:
                            synergies.append({"name": strip_markdown(match.group(1)), "effect": strip_markdown(match.group(2))})
                        i += 1
                    continue
                i += 1

            skills.append({
                "name": skill_name,
                "slug": slugify(skill_name),
                "work_in_progress": wip,
                "effects": table_rows,
                "synergies": synergies,
            })

        return skills
