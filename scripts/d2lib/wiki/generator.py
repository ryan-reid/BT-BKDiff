from __future__ import annotations
import json
import os
import re
from typing import Any, Dict, List, Optional, Tuple

from d2lib.repository import D2Repository
from d2lib.services import (
    PropertyResolverService, 
    BaseItemAnalyzerService, 
    CubeAnalyzerService, 
    MonsterAnalyzerService, 
    MiscAnalyzerService, 
    MechanicsAnalyzerService
)
from d2lib.models import (
    BaseItemFamilyDTO, 
    CubeRecipeGroupDTO, 
    MonsterActGroupDTO, 
    MiscGroupDTO, 
    MechanicsSummaryDTO
)

from d2lib.utils import slugify, strip_markdown
from d2lib.wiki.routes import (
    ITEM_FAMILIES, 
    REPORT_SOURCES, 
    WikiRoutes
)
from d2lib.wiki.renderers import WikiRenderer, WikiOutputWriter
from d2lib.wiki.builders import AreaFarmingDataBuilder, ItemIconExporter

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

    def generate(self) -> None:
        os.makedirs(self.output_dir, exist_ok=True)
        self.manifest = []
        self.writer.generated_paths = set()

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
        recipe_groups = self._load_recipe_groups()
        monster_groups = self._load_monster_groups()
        misc_groups, gem_rune_groups = self._load_misc_groups()
        mechanics_summary = self._load_mechanics_summary()

        self._write_assets()
        item_entries = self._write_item_pages(items, old_item_index)
        class_entries = self._write_class_pages(class_pages)
        self._write_runeword_index_page(items["runeword"], item_entries["runeword"])
        self._write_base_item_pages(base_item_families)
        self._write_recipe_pages(recipe_groups)
        self._write_bestiary_pages(monster_groups)
        self._write_misc_pages(misc_groups)
        self._write_gems_runes_pages(gem_rune_groups)
        self._write_mechanics_pages(mechanics_summary)
        report_entries = self._publish_reports()
        self._write_indexes(item_entries, class_entries, report_entries, area_entries, base_item_families, recipe_groups, monster_groups, misc_groups, gem_rune_groups)
        self._write_patch_notes_draft(item_entries, class_entries)
        self._write_item_index_data(item_entries, items)
        self._write_area_index_data(area_entries)
        self._write_manifest()
        self.writer.remove_stale_files()

    def _load_base_item_families(self) -> List[BaseItemFamilyDTO]:
        repo = D2Repository(self.game_data_dir)
        resolver = PropertyResolverService(repo)
        service = BaseItemAnalyzerService(repo, resolver)
        return service.analyze_base_items()

    def _write_base_item_pages(self, families: List[BaseItemFamilyDTO]) -> None:
        icon_exporter = ItemIconExporter(self.writer, self.game_data_dir, self.retail_data_dir)
        icon_exporter.attach_base_item_icons(families)
        
        # Load Retail data for comparison
        retail_repo = D2Repository(self.retail_data_dir)
        retail_resolver = PropertyResolverService(retail_repo)
        retail_service = BaseItemAnalyzerService(retail_repo, retail_resolver)
        retail_families = retail_service.analyze_base_items()
        retail_items = {item["code"]: item for f in retail_families for item in f["members"]}

        for family in families:
            for item in family["members"]:
                old_item = retail_items.get(item["code"])
                item["comparison"] = self._base_item_comparison_context(item, old_item)
                item["href"] = "" # No separate page

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
            base_classes=sorted({class_name for family in families for class_name in family["class_tags"]}),
            base_type_categories=sorted({
                category
                for family in families
                for item in family["members"]
                for category in item["type_categories"]
            }),
        )

    def _base_item_comparison_context(self, item: BaseItemDTO, old_item: Optional[BaseItemDTO]) -> Dict[str, Any]:
        if not old_item:
            return {"state": "added", "stat_rows": [], "property_rows": []}

        # 1. Stat Rows
        stat_rows = []
        stats_to_compare = [
            ("Level", "level"),
            ("Level Requirement", "level_req"),
            ("Strength Req", "str_req"),
            ("Dexterity Req", "dex_req"),
            ("Max Sockets", "sockets"),
            ("Block", "block"),
            ("Speed (WSM)", "speed"),
            ("Durability", "durability"),
        ]
        
        # Add Defense/Damage if applicable
        if item.get("defense_min") is not None or old_item.get("defense_min") is not None:
            def_old = f"{old_item.get('defense_min')}-{old_item.get('defense_max')}" if old_item.get("defense_min") is not None else ""
            def_new = f"{item.get('defense_min')}-{item.get('defense_max')}" if item.get("defense_min") is not None else ""
            stat_rows.append({"label": "Defense", "old": def_old, "new": def_new, "status": "same" if def_old == def_new else "changed"})

        if item.get("damage_min") is not None or old_item.get("damage_min") is not None:
            dam_old = f"{old_item.get('damage_min')}-{old_item.get('damage_max')}" if old_item.get("damage_min") is not None else ""
            dam_new = f"{item.get('damage_min')}-{item.get('damage_max')}" if item.get("damage_min") is not None else ""
            stat_rows.append({"label": "Damage", "old": dam_old, "new": dam_new, "status": "same" if dam_old == dam_new else "changed"})

        for label, key in stats_to_compare:
            old_val = str(old_item.get(key, ""))
            new_val = str(item.get(key, ""))
            status = "same" if old_val == new_val else "changed"
            stat_rows.append({"label": label, "old": old_val, "new": new_val, "status": status})

        # 2. Property Rows (Inherent stats, Auto Prefixes, Quality Bonuses)
        property_rows = []
        
        def add_prop_group(label, old_list, new_list):
            max_len = max(len(old_list), len(new_list))
            for i in range(max_len):
                o = old_list[i] if i < len(old_list) else ""
                n = new_list[i] if i < len(new_list) else ""
                status = "same" if o == n else "added" if n and not o else "removed" if o and not n else "changed"
                property_rows.append({"label": label if i == 0 else "", "old": o, "new": n, "status": status})

        add_prop_group("Inherent", old_item.get("inherent_stats", []), item.get("inherent_stats", []))
        add_prop_group("Auto Prefix", old_item.get("auto_prefix_summary", []), item.get("auto_prefix_summary", []))
        add_prop_group("Superior Bonuses", old_item.get("quality_bonus_summary", []), item.get("quality_bonus_summary", []))

        has_changes = any(r["status"] != "same" for r in stat_rows + property_rows)
        return {
            "state": "modified" if has_changes else "unchanged",
            "stat_rows": stat_rows,
            "property_rows": property_rows,
        }

    def _load_recipe_groups(self) -> List[CubeRecipeGroupDTO]:
        repo = D2Repository(self.game_data_dir)
        retail_repo = D2Repository(self.retail_data_dir)
        service = CubeAnalyzerService(repo, retail_repo)
        return service.analyze_all_recipes()

    def _write_recipe_pages(self, groups: List[CubeRecipeGroupDTO]) -> None:
        self._write_page(
            title=f"Cube Recipes | {self.new_label} Wiki",
            output_path=WikiRoutes.recipes_index_output_path(),
            template_name="recipes_index.html",
            category="index",
            source_files=[
                os.path.join(self.game_data_dir, "data", "global", "excel", "cubemain.txt"),
            ],
            groups=groups,
        )

    def _load_monster_groups(self) -> List[MonsterActGroupDTO]:
        repo = D2Repository(self.game_data_dir)
        retail_repo = D2Repository(self.retail_data_dir)
        service = MonsterAnalyzerService(repo, retail_repo)
        return service.analyze_monsters()

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

    def _load_misc_groups(self) -> Tuple[List[MiscGroupDTO], List[MiscGroupDTO]]:
        repo = D2Repository(self.game_data_dir)
        retail_repo = D2Repository(self.retail_data_dir)
        resolver = PropertyResolverService(repo)
        service = MiscAnalyzerService(repo, resolver, retail_repo)
        groups = service.analyze_misc_items()
        gem_rune_categories = {"Runes", "Gems & Skulls"}
        gem_rune_groups = [group for group in groups if group["category"] in gem_rune_categories]
        material_groups = [group for group in groups if group["category"] not in gem_rune_categories]
        return material_groups, gem_rune_groups

    def _write_misc_pages(self, groups: List[MiscGroupDTO]) -> None:
        ItemIconExporter(self.writer, self.game_data_dir, self.retail_data_dir).attach_misc_item_icons(groups)
        self._write_page(
            title=f"Materials | {self.new_label} Wiki",
            output_path=WikiRoutes.misc_index_output_path(),
            template_name="misc_index.html",
            category="index",
            source_files=[
                os.path.join(self.game_data_dir, "data", "global", "excel", "misc.txt"),
            ],
            groups=groups,
        )

    def _write_gems_runes_pages(self, groups: List[MiscGroupDTO]) -> None:
        icon_exporter = ItemIconExporter(self.writer, self.game_data_dir, self.retail_data_dir)
        icon_exporter.attach_misc_item_icons(groups)
        
        # Load Retail data for comparison
        retail_repo = D2Repository(self.retail_data_dir)
        retail_service = MiscAnalyzerService(retail_repo)
        retail_groups = retail_service.analyze_misc_items()
        retail_items = {item["code"]: item for g in retail_groups for item in g["members"]}

        for group in groups:
            for item in group["members"]:
                slug = slugify(item["name"])
                output_path = WikiRoutes.gem_rune_output_path(slug)
                item["href"] = WikiRoutes.route_from_output_path(output_path)
                
                old_item = retail_items.get(item["code"])
                comparison = self._gem_rune_comparison_context(item, old_item)
                
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
                            {"label": self.new_label, "tone": "accent"}
                        ],
                        "stats": stats,
                        "icon_src": item["icon_src"],
                        "source_rel_path": f"misc.txt ({item['code']})",
                        "comparison": comparison,
                    }
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

    def _gem_rune_comparison_context(self, item: MiscItemDTO, old_item: Optional[MiscItemDTO]) -> Dict[str, Any]:
        if not old_item:
            return {"state": "added", "stat_rows": [], "socket_rows": []}

        # 1. Stat Rows
        stat_rows = []
        for label, key in [("Level", "level"), ("Level Requirement", "level_req"), ("Cost", "cost")]:
            old_val = str(old_item.get(key, ""))
            new_val = str(item.get(key, ""))
            status = "same" if old_val == new_val else "changed"
            stat_rows.append({"label": label, "old": old_val, "new": new_val, "status": status})

        # 2. Socket Rows (Weapon/Armor/Shield)
        socket_rows = []
        slots = ["Weapon", "Armor/Helm", "Shield"]
        old_effects = old_item.get("socket_effects", {})
        new_effects = item.get("socket_effects", {})

        for slot in slots:
            old_eff = "; ".join(old_effects.get(slot, []))
            new_eff = "; ".join(new_effects.get(slot, []))
            status = "same" if old_eff == new_eff else "changed"
            socket_rows.append({"label": slot, "old": old_eff, "new": new_eff, "status": status})

        has_changes = any(r["status"] != "same" for r in stat_rows + socket_rows)
        return {
            "state": "modified" if has_changes else "unchanged",
            "stat_rows": stat_rows,
            "property_rows": socket_rows, # Reuse template property_rows block for simplicity
        }

    def _load_mechanics_summary(self) -> MechanicsSummaryDTO:
        repo = D2Repository(self.game_data_dir)
        retail_repo = D2Repository(self.retail_data_dir)
        service = MechanicsAnalyzerService(repo, retail_repo)
        return service.analyze_mechanics()

    def _write_mechanics_pages(self, summary: MechanicsSummaryDTO) -> None:
        self._write_page(
            title=f"Mechanics & Progression | {self.new_label} Wiki",
            output_path=WikiRoutes.mechanics_output_path(),
            template_name="mechanics.html",
            category="index",
            source_files=[
                os.path.join(self.game_data_dir, "data", "global", "excel", "experience.txt"),
                os.path.join(self.game_data_dir, "data", "global", "excel", "difficultylevels.txt"),
                os.path.join(self.game_data_dir, "data", "global", "excel", "skills.txt"),
                os.path.join(self.game_data_dir, "data", "global", "excel", "missiles.txt"),
                os.path.join(self.game_data_dir, "data", "global", "excel", "charstats.txt"),
                os.path.join(self.game_data_dir, "data", "global", "excel", "properties.txt"),
                os.path.join(self.game_data_dir, "data", "global", "excel", "itemstatcost.txt"),
                os.path.join(self.game_data_dir, "data", "global", "excel", "gamble.txt"),
            ],
            summary=summary,
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
                    if self._should_include_item(record, family):
                        items[family].append(record)

        return items

    def _index_items(self, items: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Dict[str, Dict[str, Any]]]:
        index: Dict[str, Dict[str, Dict[str, Any]]] = {family: {} for family in ITEM_FAMILIES}
        for family, entries in items.items():
            for entry in entries:
                index[family][self._item_identity(entry, family)] = entry
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
            pages.append(
                {
                    "class_name": class_name,
                    "skills": self._parse_skill_tree_markdown(content),
                    "source_path": full_path,
                }
            )

        return pages

    def _load_area_entries(self) -> List[Dict[str, Any]]:
        if not os.path.isdir(self.game_data_dir):
            return []
        return AreaFarmingDataBuilder(self.game_data_dir, layout_data_dir=self.layout_data_dir).build()

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
                        parts = [part.strip() for part in row_line.strip("|").split("|")]
                        if len(parts) >= 7:
                            table_rows.append(
                                {
                                    "effect": strip_markdown(parts[0]),
                                    "scaling": strip_markdown(parts[1]),
                                    "l1": strip_markdown(parts[2]),
                                    "l10": strip_markdown(parts[3]),
                                    "l20": strip_markdown(parts[4]),
                                    "l20_soft10": strip_markdown(parts[5]),
                                    "limit": strip_markdown(parts[6]),
                                }
                            )
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
                            synergies.append(
                                {
                                    "name": strip_markdown(match.group(1)),
                                    "effect": strip_markdown(match.group(2)),
                                }
                            )
                        i += 1
                    continue
                i += 1

            skills.append(
                {
                    "name": skill_name,
                    "slug": slugify(skill_name),
                    "work_in_progress": wip,
                    "effects": table_rows,
                    "synergies": synergies,
                }
            )

        return skills

    def _write_assets(self) -> None:
        ASSET_SOURCE_DIR = os.path.join(MODULE_DIR, "..", "wiki_assets")
        if not os.path.isdir(ASSET_SOURCE_DIR):
             ASSET_SOURCE_DIR = os.path.join(D2LIB_DIR, "wiki_assets")
             
        for filename in sorted(os.listdir(ASSET_SOURCE_DIR)):
            source_path = os.path.join(ASSET_SOURCE_DIR, filename)
            if os.path.isfile(source_path):
                self.writer.copy_asset(source_path, f"assets/{filename}")

    def _write_item_pages(
        self,
        items: Dict[str, List[Dict[str, Any]]],
        old_item_index: Dict[str, Dict[str, Dict[str, Any]]],
    ) -> Dict[str, List[Dict[str, str]]]:
        page_entries: Dict[str, List[Dict[str, str]]] = {family: [] for family in ITEM_FAMILIES}
        used_paths: Dict[str, Dict[str, int]] = {family: {} for family in ITEM_FAMILIES}
        icon_exporter = ItemIconExporter(self.writer, self.game_data_dir, self.retail_data_dir)

        for family, entries in items.items():
            for entry in sorted(entries, key=self._item_sort_key):
                title = self._item_title(entry, family)
                old_entry = old_item_index.get(family, {}).get(self._item_identity(entry, family))
                status = self._item_diff_status(entry, old_entry)
                slug = self._item_slug(entry, family, title, used_paths[family])
                output_path = WikiRoutes.item_output_path(family, slug)
                href = WikiRoutes.route_from_output_path(output_path)
                icon_src = icon_exporter.export_entry_icon(entry, family)
                entry["icon_src"] = icon_src
                if family == "runeword":
                    entry["rune_requirements"] = self._runeword_rune_requirements(entry, icon_exporter)
                page_entries[family].append(
                    {
                        "title": title,
                        "href": href,
                        "summary": self._item_summary(entry, family),
                        "search_text": self._item_search_text(entry, family),
                        "status": status,
                        "item_group": self._item_filter_group(entry, family),
                        "item_type": self._item_filter_type(entry, family),
                        "icon_src": icon_src,
                    }
                )

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
            entries.append(
                {
                    "title": title,
                    "href": href,
                    "summary": f"{len(page['skills'])} generated skill entries",
                    "search_text": f"{title} {' '.join(skill['name'] for skill in page['skills'])}",
                }
            )
        return entries

    def _write_runeword_index_page(
        self,
        runewords: List[Dict[str, Any]],
        page_entries: List[Dict[str, str]],
    ) -> None:
        href_by_title = {entry["title"]: entry for entry in page_entries}
        icon_exporter = ItemIconExporter(self.writer, self.game_data_dir, self.retail_data_dir)
        records = []

        for entry in sorted(runewords, key=self._item_sort_key):
            title = self._item_title(entry, "runeword")
            page_entry = href_by_title.get(title, {})
            rune_requirements = entry.get("rune_requirements") or self._runeword_rune_requirements(
                entry, icon_exporter
            )

            property_preview = [
                str(prop.get("resolved_text", ""))
                for prop in entry.get("properties", [])
                if str(prop.get("resolved_text", "")).strip()
            ][:5]

            records.append(
                {
                    "title": title,
                    "href": page_entry.get("href", ""),
                    "status": page_entry.get("status", "unchanged"),
                    "summary": self._item_summary(entry, "runeword"),
                    "base_items": entry.get("base_items", []),
                    "runes": rune_requirements,
                    "properties": property_preview,
                    "search_text": " ".join(
                        [
                            title,
                            " ".join(entry.get("base_items", [])),
                            " ".join(rune["name"] for rune in rune_requirements),
                            " ".join(rune["code"] for rune in rune_requirements),
                            " ".join(property_preview),
                            page_entry.get("status", ""),
                        ]
                    ),
                }
            )

        self._write_page(
            title=f"Runewords | {self.new_label} Wiki",
            output_path=WikiRoutes.runewords_index_output_path(),
            template_name="runewords_index.html",
            category="index",
            source_files=[os.path.join(self.game_data_dir, "data", "global", "excel", "runes.txt")],
            runewords=records,
        )

    @staticmethod
    def _runeword_rune_name(entry: Dict[str, Any], rune_code: str, rune_index: int) -> str:
        runes = entry.get("runes", [])
        if rune_index < len(runes):
            return str(runes[rune_index])
        return rune_code

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
            rune_name = self._runeword_rune_name(entry, rune_code, len(requirements))
            requirements.append(
                {
                    "code": rune_code,
                    "name": rune_name,
                    "icon_src": icon_exporter.export_icon(
                        output_key=f"rune-{rune_code}",
                        item_code=rune_code,
                        icon_key=rune_code,
                    ),
                }
            )

        if requirements:
            return requirements

        return [
            {
                "code": "",
                "name": str(rune_name),
                "icon_src": "",
            }
            for rune_name in entry.get("runes", [])
        ]

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
            total_items=sum(len(entries) for entries in item_entries.values()),
            reports=report_entries,
        )

        group_to_types: Dict[str, set[str]] = {}
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
            item_groups=[
                {"name": group, "types": sorted(group_to_types[group])}
                for group in sorted(group_to_types)
            ],
        )

        self._write_page(
            title=f"Classes | {self.new_label} Data Wiki",
            output_path=WikiRoutes.classes_index_output_path(),
            template_name="classes_index.html",
            category="index",
            source_files=[],
            classes=class_entries,
        )

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

        self._write_page(
            title=f"Reports | {self.new_label} Data Wiki",
            output_path=WikiRoutes.reports_index_output_path(),
            template_name="reports_index.html",
            category="index",
            source_files=[],
            reports=report_entries,
        )

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
        # Helper to find properties for a page entry
        prop_map = {}
        for family in ("unique", "set"):
            for item in items[family]:
                key = (family, item.get("display_name") or item.get("name") or item.get("id"))
                prop_map[key] = [p["resolved_text"] for p in item.get("properties", []) if p.get("resolved_text")][:5]

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
                "properties": prop_map.get((family, entry["title"]), []),
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
                    rel_output = f"{report['output_dir']}/{rel_source}"
                    self.writer.copy_asset(source_path, rel_output)
                    copied_files += 1

            if copied_files == 0:
                continue

            href = WikiRoutes.route_from_output_path(f"{report['output_dir']}/index.html")
            entry = {
                "title": report["title"],
                "href": href,
                "summary": report["description"],
                "source_dir": report["source_dir"],
                "source_kind": report["source_kind"],
                "file_count": str(copied_files),
            }
            entries.append(entry)
            self.manifest.append(
                {
                    "title": report["title"],
                    "path": href,
                    "category": "report",
                    "sources": [report["source_dir"]],
                }
            )
        return entries

    def _write_manifest(self) -> None:
        self.writer.write_text("manifest.json", json.dumps(self.manifest, indent=2))

    def _write_page(
        self,
        title: str,
        output_path: str,
        template_name: str,
        category: str,
        source_files: List[str],
        **context: Any,
    ) -> None:
        document = self.renderer.render(
            template_name,
            title=title,
            site_root=WikiRoutes.site_root_for_output_path(output_path),
            old_label=self.old_label,
            new_label=self.new_label,
            **context,
        )
        self.writer.write_text(output_path, document)
        self.manifest.append(
            {
                "title": title,
                "path": WikiRoutes.route_from_output_path(output_path),
                "category": category,
                "sources": source_files,
            }
        )

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
            chips.append(
                {
                    "label": "Set Item" if family == "set" else entry.get("item_type", "Item"),
                    "tone": "accent",
                }
            )
            stats = [
                {"label": "Base Item", "value": entry.get("base_item", "Unknown")},
                {"label": "Item Type", "value": entry.get("item_type", "Unknown")},
                {"label": "Level Requirement", "value": entry.get("lvl_req", "0")},
            ]
            if family == "set" and entry.get("raw_row", {}).get("set"):
                stats.append({"label": "Set", "value": entry["raw_row"]["set"]})

        properties = [
            {
                "text": str(prop.get("resolved_text", "")),
                "is_warning": "unknown property:" in str(prop.get("resolved_text", "")).lower(),
            }
            for prop in entry.get("properties", [])
        ]
        rune_properties = [
            {
                "rune": str(rune_entry.get("rune", "")),
                "properties": [
                    {
                        "text": str(prop.get("resolved_text", "")),
                        "is_warning": "unknown property:" in str(prop.get("resolved_text", "")).lower(),
                    }
                    for prop in rune_entry.get("properties", [])
                ],
            }
            for rune_entry in entry.get("rune_properties", [])
        ]
        comparison = self._item_comparison_context(entry, family, old_entry)
        return {
            "family": family,
            "title": title,
            "hero_eyebrow": hero_eyebrow,
            "summary": self._item_summary(entry, family),
            "chips": chips,
            "stats": stats,
            "properties": properties,
            "rune_properties": rune_properties,
            "rune_requirements": entry.get("rune_requirements", []),
            "base_filter_url": self._runeword_base_filter_url(entry, len(entry.get("rune_requirements", []))),
            "old_base_label": ", ".join(old_entry.get("base_items", [])) if old_entry else "",
            "old_rune_label": " + ".join(old_entry.get("runes", [])) if old_entry else "",
            "required_level": entry.get("required_level", ""),
            "runeword_compare_rows": self._runeword_compare_rows(entry, old_entry),
            "icon_src": entry.get("icon_src", ""),
            "source_rel_path": entry.get("_source_rel_path", ""),
            "comparison": comparison,
            "comparison_summary": self._comparison_summary_context(comparison),
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
        from urllib.parse import urlencode
        return f"bases/?{urlencode(params)}" if params else "bases/"

    @staticmethod
    def _runeword_compare_rows(
        entry: Dict[str, Any],
        old_entry: Optional[Dict[str, Any]],
    ) -> List[Dict[str, str]]:
        old_props = WikiGenerator._property_occurrence_map(old_entry or {})
        new_props = WikiGenerator._property_occurrence_map(entry)
        keys = list(new_props.keys()) + [key for key in old_props.keys() if key not in new_props]
        rows = []
        for key in keys:
            old_value = old_props.get(key, "")
            new_value = new_props.get(key, "")
            if old_value and new_value:
                status = "changed" if old_value != new_value else "same"
            elif new_value:
                status = "added"
            elif old_value:
                status = "removed"
            else:
                status = "same"
            rows.append({"old": old_value, "new": new_value, "status": status})
            
        old_rune_props = WikiGenerator._rune_property_occurrence_map(old_entry or {})
        new_rune_props = WikiGenerator._rune_property_occurrence_map(entry)
        if old_rune_props or new_rune_props:
            rows.append({"old": "", "new": "", "status": "separator"})
            rune_keys = list(new_rune_props.keys()) + [key for key in old_rune_props.keys() if key not in new_rune_props]
            for key in rune_keys:
                old_value = old_rune_props.get(key, "")
                new_value = new_rune_props.get(key, "")
                if old_value and new_value:
                    status = "changed" if old_value != new_value else "same"
                elif new_value:
                    status = "added"
                elif old_value:
                    status = "removed"
                else:
                    status = "same"
                rows.append({"old": old_value, "new": new_value, "status": status})
        return rows

    @staticmethod
    def _rune_property_occurrence_map(entry: Dict[str, Any]) -> Dict[Tuple[str, str, int], str]:
        occurrences: Dict[Tuple[str, str], int] = {}
        values: Dict[Tuple[str, str, int], str] = {}
        for rune_entry in entry.get("rune_properties", []):
            for prop in rune_entry.get("properties", []):
                code = str(prop.get("code", "")).strip() or "unknown"
                param = str(prop.get("param", "")).strip()
                text = str(prop.get("resolved_text", "")).strip()
                if not text:
                    continue
                base_key = (code, param)
                occurrences[base_key] = occurrences.get(base_key, 0) + 1
                values[(code, param, occurrences[base_key])] = text
        return values

    def _item_comparison_context(
        self,
        entry: Dict[str, Any],
        family: str,
        old_entry: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        if old_entry is None:
            return {"state": "added", "rows": []}

        # 1. Stat Rows (Base, Lvl Req, etc.)
        stat_rows = []
        for label, old_value, new_value in self._comparison_stat_rows(entry, family, old_entry):
            status = "same" if old_value == new_value else "changed"
            stat_rows.append({"label": label, "old": old_value, "new": new_value, "status": status})

        # 2. Property Rows (Aligned side-by-side)
        property_rows = []
        old_props = WikiGenerator._property_occurrence_map(old_entry)
        new_props = WikiGenerator._property_occurrence_map(entry)
        all_keys = list(new_props.keys()) + [key for key in old_props.keys() if key not in new_props]
        
        for key in all_keys:
            old_val = old_props.get(key, "")
            new_val = new_props.get(key, "")
            
            if old_val and new_val:
                status = "changed" if old_val != new_val else "same"
            elif new_val:
                status = "added"
            elif old_val:
                status = "removed"
            else:
                status = "same"
                
            property_rows.append({
                "label": WikiGenerator._comparison_property_label(old_val, new_val, key[0], key[2]),
                "old": old_val,
                "new": new_val,
                "status": status
            })

        has_changes = any(r["status"] != "same" for r in stat_rows + property_rows)
        
        return {
            "state": "modified" if has_changes else "unchanged",
            "stat_rows": stat_rows,
            "property_rows": property_rows,
            # Legacy rows for existing template compatibility during transition
            "rows": [r for r in stat_rows + property_rows if r["status"] != "same"]
        }

    @staticmethod
    def _comparison_summary_context(comparison: Dict[str, Any]) -> Dict[str, Any]:
        summary = {"added": [], "removed": [], "changed": []}
        for row in comparison.get("rows", []):
            label = str(row.get("label", ""))
            old_value = str(row.get("old", ""))
            new_value = str(row.get("new", ""))
            if label == "Property Count":
                continue
            if label.startswith("Added:") and new_value:
                summary["added"].append({"label": label.replace("Added:", "").strip(), "value": new_value})
            elif label.startswith("Removed:") and old_value:
                summary["removed"].append({"label": label.replace("Removed:", "").strip(), "value": old_value})
            elif old_value != new_value:
                summary["changed"].append({"label": label, "old": old_value, "new": new_value})
        summary["has_changes"] = any(summary[key] for key in ("added", "removed", "changed"))
        return summary

    @staticmethod
    def _item_sort_key(entry: Dict[str, Any]) -> str:
        return (entry.get("display_name") or entry.get("name") or entry.get("id") or "").lower()

    @staticmethod
    def _item_identity(entry: Dict[str, Any], family: str) -> str:
        title = entry.get("display_name") or entry.get("name") or entry.get("id") or ""
        if family == "runeword":
            return title
        if family == "set":
            set_name = entry.get("raw_row", {}).get("set", "")
            return f"{title}|{entry.get('base_item', '')}|{set_name}"
        return f"{title}|{entry.get('base_item', '')}"

    @staticmethod
    def _item_diff_status(entry: Dict[str, Any], old_entry: Optional[Dict[str, Any]]) -> str:
        if old_entry is None:
            return "added"
        if WikiGenerator._entries_match(entry, old_entry):
            return "unchanged"
        return "modified"

    @staticmethod
    def _entries_match(entry: Dict[str, Any], old_entry: Dict[str, Any]) -> bool:
        keys = ["base_item", "item_type", "lvl_req"]
        if any(str(entry.get(key, "")) != str(old_entry.get(key, "")) for key in keys):
            return False
        return WikiGenerator._property_texts(entry) == WikiGenerator._property_texts(old_entry)

    @staticmethod
    def _property_texts(entry: Dict[str, Any]) -> List[str]:
        return [str(prop.get("resolved_text", "")) for prop in entry.get("properties", [])]

    @staticmethod
    def _comparison_stat_rows(
        entry: Dict[str, Any],
        family: str,
        old_entry: Dict[str, Any],
    ) -> List[Tuple[str, str, str]]:
        if family == "runeword":
            return [
                ("Runes", " + ".join(old_entry.get("runes", [])), " + ".join(entry.get("runes", []))),
                ("Base Items", ", ".join(old_entry.get("base_items", [])), ", ".join(entry.get("base_items", []))),
                ("Property Count", str(len(old_entry.get("properties", []))), str(len(entry.get("properties", [])))),
            ]

        fields = [
            ("Base Item", str(old_entry.get("base_item", "")), str(entry.get("base_item", ""))),
            ("Item Type", str(old_entry.get("item_type", "")), str(entry.get("item_type", ""))),
            ("Level Requirement", str(old_entry.get("lvl_req", "")), str(entry.get("lvl_req", ""))),
        ]
        if family == "set":
            fields.append(
                (
                    "Set",
                    str(old_entry.get("raw_row", {}).get("set", "")),
                    str(entry.get("raw_row", {}).get("set", "")),
                )
            )
        return fields

    @staticmethod
    def _comparison_property_rows(
        entry: Dict[str, Any],
        old_entry: Dict[str, Any],
    ) -> List[Tuple[str, str, str]]:
        old_props = WikiGenerator._property_occurrence_map(old_entry)
        new_props = WikiGenerator._property_occurrence_map(entry)
        all_keys = list(new_props.keys()) + [key for key in old_props.keys() if key not in new_props]
        return [
            (
                WikiGenerator._comparison_property_label(
                    old_props.get(key, ""),
                    new_props.get(key, ""),
                    key[0],
                    key[2],
                ),
                old_props.get(key, ""),
                new_props.get(key, ""),
            )
            for key in all_keys
        ]

    @staticmethod
    def _property_occurrence_map(entry: Dict[str, Any]) -> Dict[Tuple[str, str, int], str]:
        occurrences: Dict[Tuple[str, str], int] = {}
        values: Dict[Tuple[str, str, int], str] = {}
        for prop in entry.get("properties", []):
            code = str(prop.get("code", "")).strip() or "unknown"
            param = str(prop.get("param", "")).strip()
            base_key = (code, param)
            occurrences[base_key] = occurrences.get(base_key, 0) + 1
            values[(code, param, occurrences[base_key])] = str(prop.get("resolved_text", "")).strip()
        return values

    @staticmethod
    def _comparison_property_label(old_value: str, new_value: str, code: str, occurrence: int) -> str:
        old_label = WikiGenerator._comparison_text_label(old_value)
        new_label = WikiGenerator._comparison_text_label(new_value)
        if old_value and new_value:
            if old_label and old_label == new_label:
                return old_label
            if old_label and new_label:
                return f"{old_label} / {new_label}"
            return f"Changed Stat #{occurrence}"
        if new_value:
            return f"Added: {new_label or code}"
        if old_value:
            return f"Removed: {old_label or code}"
        return f"Stat #{occurrence}"

    @staticmethod
    def _comparison_text_label(value: str) -> str:
        if not value:
            return ""
        text = str(value)
        text = re.sub(r"Unknown property:\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\([^)]*\)", " ", text)
        text = re.sub(r"[-+]?\d+(?:\.\d+)?", " ", text)
        text = re.sub(r"[%#/]+", " ", text)
        text = re.sub(r"\s+", " ", text).strip(" -")
        return text[:1].upper() + text[1:] if text else ""

    @staticmethod
    def _should_include_item(entry: Dict[str, Any], family: str) -> bool:
        properties = entry.get("properties", [])
        if family == "runeword":
            base_items = [str(base).strip() for base in entry.get("base_items", []) if str(base).strip()]
            runes = [str(rune).strip() for rune in entry.get("runes", []) if str(rune).strip()]
            if not properties and not runes:
                if not base_items or all(base.lower() == "expansion" for base in base_items):
                    return False
            return True

        title = str(entry.get("display_name") or entry.get("id") or entry.get("name") or "").strip()
        base_item = str(entry.get("base_item", "")).strip()
        item_type = str(entry.get("item_type", "")).strip()
        if not properties:
            if title.lower() == "blank charm":
                return False
            if base_item.lower() == "expansion" and item_type.lower() == "expansion":
                return False
        return True

    @staticmethod
    def _item_title(entry: Dict[str, Any], family: str) -> str:
        if family == "runeword":
            return entry.get("name", "Unknown Runeword")
        return entry.get("display_name") or entry.get("id") or entry.get("name") or "Unknown Item"

    @staticmethod
    def _item_summary(entry: Dict[str, Any], family: str) -> str:
        if family == "runeword":
            base_items = ", ".join(entry.get("base_items", [])) or "Unknown base"
            runes = " + ".join(entry.get("runes", [])) or "unknown runes"
            socket_count = len(entry.get("runes", []))
            socket_text = f"{socket_count}-socket " if socket_count else ""
            return f"{runes} in {socket_text}{base_items}."
        item_type = entry.get("item_type", "Item")
        base_item = entry.get("base_item", "Unknown base")
        lvl_req = entry.get("lvl_req", "0")
        return f"{item_type} based on {base_item}. Level requirement {lvl_req}."

    @staticmethod
    def _item_search_text(entry: Dict[str, Any], family: str) -> str:
        if family == "runeword":
            runes = " ".join(entry.get("runes", []))
            bases = " ".join(entry.get("base_items", []))
            props = " ".join(prop.get("resolved_text", "") for prop in entry.get("properties", []))
            return f"{entry.get('name', '')} {runes} {bases} {props}"
        props = " ".join(prop.get("resolved_text", "") for prop in entry.get("properties", []))
        return (
            f"{entry.get('display_name', '')} "
            f"{entry.get('base_item', '')} "
            f"{entry.get('item_type', '')} "
            f"{entry.get('raw_row', {}).get('set', '')} "
            f"{props}"
        )

    @staticmethod
    def _item_filter_type(entry: Dict[str, Any], family: str) -> str:
        if family == "runeword":
            base_items = entry.get("base_items", [])
            return str(base_items[0]) if base_items else "Runeword"
        return str(entry.get("item_type", "")).strip() or "Item"

    @staticmethod
    def _item_filter_group(entry: Dict[str, Any], family: str) -> str:
        category = WikiGenerator._item_filter_type(entry, family).lower()
        if any(token in category for token in ["amazon", "assassin", "orb", "hand to hand", "grimoire"]):
            return "Class Weapons"
        if "axe" in category:
            return "Axes"
        if "crossbow" in category:
            return "Crossbows"
        if "bow" in category:
            return "Bows"
        if "dagger" in category or "knife" in category:
            return "Daggers"
        if "javelin" in category:
            return "Javelins"
        if "mace" in category or "club" in category or "hammer" in category:
            return "Maces"
        if "polearm" in category:
            return "Polearms"
        if "scepter" in category:
            return "Scepters"
        if "spear" in category:
            return "Spears"
        if "staff" in category:
            return "Staves"
        if "sword" in category:
            return "Swords"
        if "throwing" in category:
            return "Throwing"
        if "wand" in category:
            return "Wands"
        if any(token in category for token in ["voodoo", "pelt", "primal", "auric"]):
            return "Class Armors"
        if "amulet" in category:
            return "Amulets"
        if "ring" in category:
            return "Rings"
        if "charm" in category:
            return "Charms"
        if "jewel" in category:
            return "Jewels"
        if any(token in category for token in ["helm", "circlet", "merc"]):
            return "Helms"
        if any(token in category for token in ["armor", "tors"]):
            return "Chests"
        if "shield" in category:
            return "Shields"
        if "glove" in category:
            return "Gloves"
        if "belt" in category:
            return "Belts"
        if "boot" in category:
            return "Boots"
        return "Others"

    @staticmethod
    def _item_slug(entry: Dict[str, Any], family: str, title: str, used_paths: Dict[str, int]) -> str:
        base_slug = slugify(title)
        if family == "runeword":
            disambiguator = entry.get("base_items", [""])[0]
        else:
            disambiguator = entry.get("base_item") or entry.get("id") or ""

        candidate = base_slug
        if candidate in used_paths:
            disambiguation_slug = slugify(disambiguator)
            if disambiguation_slug:
                candidate = f"{base_slug}-{disambiguation_slug}"
        root_candidate = candidate
        suffix = 2
        while candidate in used_paths:
            candidate = f"{root_candidate}-{suffix}"
            suffix += 1
        used_paths[candidate] = 1
        return candidate