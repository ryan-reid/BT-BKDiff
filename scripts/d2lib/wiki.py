import json
import os
import re
import shutil
from typing import Any, Dict, List, Optional, Tuple

from jinja2 import Environment, FileSystemLoader, select_autoescape


MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(MODULE_DIR, "wiki_templates")
ASSET_SOURCE_DIR = os.path.join(MODULE_DIR, "wiki_assets")
ITEM_FAMILIES = ("unique", "set", "runeword")


def _slugify(value: str) -> str:
    text = value.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[-\s]+", "-", text)
    return text.strip("-") or "untitled"


def _strip_markdown_markup(value: str) -> str:
    text = value.replace("\\+", "+")
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"`(.*?)`", r"\1", text)
    return text.strip()


class WikiRoutes:
    @staticmethod
    def home_output_path() -> str:
        return "index.html"

    @staticmethod
    def items_index_output_path() -> str:
        return "items/index.html"

    @staticmethod
    def item_output_path(family: str, slug: str) -> str:
        return f"items/{family}/{slug}/index.html"

    @staticmethod
    def classes_index_output_path() -> str:
        return "classes/index.html"

    @staticmethod
    def class_output_path(slug: str) -> str:
        return f"classes/{slug}/index.html"

    @staticmethod
    def patch_notes_output_path() -> str:
        return "patch-notes/full-patch-notes-draft/index.html"

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


class WikiRenderer:
    def __init__(self, template_dir: str = TEMPLATE_DIR):
        self.environment = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def render(self, template_name: str, **context: Any) -> str:
        return self.environment.get_template(template_name).render(**context)


class WikiOutputWriter:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        self.generated_paths: set[str] = set()

    def write_text(self, relative_path: str, content: str) -> None:
        normalized = relative_path.replace("\\", "/")
        full_path = os.path.join(self.output_dir, normalized)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        self.generated_paths.add(normalized)

    def copy_asset(self, source_path: str, relative_path: str) -> None:
        normalized = relative_path.replace("\\", "/")
        full_path = os.path.join(self.output_dir, normalized)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        shutil.copyfile(source_path, full_path)
        self.generated_paths.add(normalized)

    def remove_stale_files(self) -> None:
        for root, dirs, files in os.walk(self.output_dir, topdown=False):
            for filename in files:
                full_path = os.path.join(root, filename)
                rel_path = os.path.relpath(full_path, self.output_dir).replace("\\", "/")
                if rel_path in self.generated_paths:
                    continue
                try:
                    os.remove(full_path)
                except OSError:
                    pass

            for dirname in dirs:
                dir_path = os.path.join(root, dirname)
                try:
                    os.rmdir(dir_path)
                except OSError:
                    pass


class WikiGenerator:
    def __init__(
        self,
        item_db_dir: str,
        skill_tree_dir: str,
        output_dir: str,
        old_item_db_dir: Optional[str] = None,
        old_label: str = "Retail",
        new_label: str = "BKDiablo",
    ):
        self.item_db_dir = item_db_dir
        self.skill_tree_dir = skill_tree_dir
        self.output_dir = output_dir
        self.old_item_db_dir = old_item_db_dir
        self.old_label = old_label
        self.new_label = new_label
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

        self._write_assets()
        item_entries = self._write_item_pages(items, old_item_index)
        class_entries = self._write_class_pages(class_pages)
        self._write_indexes(item_entries, class_entries)
        self._write_patch_notes_draft(item_entries, class_entries)
        self._write_item_index_data(item_entries)
        self._write_manifest()
        self.writer.remove_stale_files()

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
                                    "effect": _strip_markdown_markup(parts[0]),
                                    "scaling": _strip_markdown_markup(parts[1]),
                                    "l1": _strip_markdown_markup(parts[2]),
                                    "l10": _strip_markdown_markup(parts[3]),
                                    "l20": _strip_markdown_markup(parts[4]),
                                    "l20_soft10": _strip_markdown_markup(parts[5]),
                                    "limit": _strip_markdown_markup(parts[6]),
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
                                    "name": _strip_markdown_markup(match.group(1)),
                                    "effect": _strip_markdown_markup(match.group(2)),
                                }
                            )
                        i += 1
                    continue
                i += 1

            skills.append(
                {
                    "name": skill_name,
                    "slug": _slugify(skill_name),
                    "work_in_progress": wip,
                    "effects": table_rows,
                    "synergies": synergies,
                }
            )

        return skills

    def _write_assets(self) -> None:
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

        for family, entries in items.items():
            for entry in sorted(entries, key=self._item_sort_key):
                title = self._item_title(entry, family)
                old_entry = old_item_index.get(family, {}).get(self._item_identity(entry, family))
                status = self._item_diff_status(entry, old_entry)
                slug = self._item_slug(entry, family, title, used_paths[family])
                output_path = WikiRoutes.item_output_path(family, slug)
                href = WikiRoutes.route_from_output_path(output_path)
                page_entries[family].append(
                    {
                        "title": title,
                        "href": href,
                        "summary": self._item_summary(entry, family),
                        "search_text": self._item_search_text(entry, family),
                        "status": status,
                        "item_group": self._item_filter_group(entry, family),
                        "item_type": self._item_filter_type(entry, family),
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
            output_path = WikiRoutes.class_output_path(_slugify(title))
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

    def _write_indexes(
        self,
        item_entries: Dict[str, List[Dict[str, str]]],
        class_entries: List[Dict[str, str]],
    ) -> None:
        self._write_page(
            title="BT Diablo Data Wiki",
            output_path=WikiRoutes.home_output_path(),
            template_name="home.html",
            category="index",
            source_files=[],
            item_counts={family: len(item_entries[family]) for family in ITEM_FAMILIES},
            class_count=len(class_entries),
            total_items=sum(len(entries) for entries in item_entries.values()),
        )

        group_to_types: Dict[str, set[str]] = {}
        for entries in item_entries.values():
            for entry in entries:
                group_to_types.setdefault(entry["item_group"], set()).add(entry["item_type"])

        self._write_page(
            title="All Items | BT Diablo Data Wiki",
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
            title="Classes | BT Diablo Data Wiki",
            output_path=WikiRoutes.classes_index_output_path(),
            template_name="classes_index.html",
            category="index",
            source_files=[],
            classes=class_entries,
        )

    def _write_patch_notes_draft(
        self,
        item_entries: Dict[str, List[Dict[str, str]]],
        class_entries: List[Dict[str, str]],
    ) -> None:
        self._write_page(
            title="Full Patch Notes Draft | BT Diablo Data Wiki",
            output_path=WikiRoutes.patch_notes_output_path(),
            template_name="patch_notes.html",
            category="patch",
            source_files=[],
            total_items=sum(len(entries) for entries in item_entries.values()),
            class_count=len(class_entries),
        )

    def _write_item_index_data(self, item_entries: Dict[str, List[Dict[str, str]]]) -> None:
        rows = [
            {
                "title": entry["title"],
                "href": entry["href"],
                "family": family,
                "status": entry["status"],
                "item_group": entry["item_group"],
                "item_type": entry["item_type"],
                "summary": entry["summary"],
                "search_text": entry["search_text"],
            }
            for family in ITEM_FAMILIES
            for entry in item_entries[family]
        ]
        self.writer.write_text("data/items-index.json", json.dumps(rows, indent=2))

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
        if family == "runeword":
            chips.append({"label": "Runeword", "tone": "accent"})
            stats = [
                {"label": "Runes", "value": " + ".join(entry.get("runes", [])) or "Unknown"},
                {"label": "Base Items", "value": ", ".join(entry.get("base_items", [])) or "Unknown"},
                {"label": "Property Count", "value": str(len(entry.get("properties", [])))},
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
        return {
            "title": title,
            "summary": self._item_summary(entry, family),
            "chips": chips,
            "stats": stats,
            "properties": properties,
            "rune_properties": rune_properties,
            "source_rel_path": entry.get("_source_rel_path", ""),
            "comparison": self._item_comparison_context(entry, family, old_entry),
        }

    def _item_comparison_context(
        self,
        entry: Dict[str, Any],
        family: str,
        old_entry: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        if old_entry is None:
            return {"state": "added", "rows": []}

        rows: List[Tuple[str, str, str]] = []
        for label, old_value, new_value in self._comparison_stat_rows(entry, family, old_entry):
            if old_value != new_value:
                rows.append((label, old_value, new_value))
        for label, old_value, new_value in self._comparison_property_rows(entry, old_entry):
            if old_value != new_value:
                rows.append((label, old_value, new_value))
        return {
            "state": "modified" if rows else "unchanged",
            "rows": [{"label": label, "old": old_value, "new": new_value} for label, old_value, new_value in rows],
        }

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
            return f"Runeword for {base_items} with {len(entry.get('properties', []))} generated properties."
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
        base_slug = _slugify(title)
        if family == "runeword":
            disambiguator = entry.get("base_items", [""])[0]
        else:
            disambiguator = entry.get("base_item") or entry.get("id") or ""

        candidate = base_slug
        if candidate in used_paths:
            disambiguation_slug = _slugify(disambiguator)
            if disambiguation_slug:
                candidate = f"{base_slug}-{disambiguation_slug}"
        root_candidate = candidate
        suffix = 2
        while candidate in used_paths:
            candidate = f"{root_candidate}-{suffix}"
            suffix += 1
        used_paths[candidate] = 1
        return candidate
