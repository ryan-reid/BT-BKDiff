from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List

from d2lib.wiki.publication import WikiPageDTO, WikiSiteDTO
from d2lib.wiki.routes import WikiRoutes


class MediaWikiRenderer:
    """Renders shared wiki page DTOs as deterministic MediaWiki wikitext."""

    def render_page(self, page: WikiPageDTO, site: WikiSiteDTO) -> str:
        kind = page["kind"]
        payload = page["payload"]
        title = self.page_title(page)
        lines = [f"= {self._text(title)} =", ""]

        render_method = getattr(self, f"_render_{kind}", None)
        if render_method:
            lines.extend(render_method(payload, site))
        else:
            lines.extend(self._render_generic(payload))

        sources = page.get("source_files", [])
        if sources:
            lines.extend(["", "== Sources ==", *[f"* <code>{self._text(source)}</code>" for source in sources]])
        return "\n".join(lines).rstrip() + "\n"

    def page_title(self, page: WikiPageDTO) -> str:
        page_payload = page["payload"].get("page")
        if isinstance(page_payload, dict) and page_payload.get("title"):
            return str(page_payload["title"])
        return str(page["title"]).split("|", 1)[0].strip()

    def output_path_for_page(self, page: WikiPageDTO) -> str:
        route = WikiRoutes.route_from_output_path(page["output_path"]).strip("/") or "home"
        safe = re.sub(r"[^a-zA-Z0-9_.-]+", "_", route.replace("/", "__")).strip("_") or "home"
        return f"{safe}.wiki"

    def should_publish_page(self, page: WikiPageDTO) -> bool:
        return page["kind"] != "item"

    def manifest_entry(self, page: WikiPageDTO) -> Dict[str, Any]:
        return {
            "title": self.page_title(page),
            "route": WikiRoutes.route_from_output_path(page["output_path"]),
            "html_path": page["output_path"],
            "mediawiki_path": self.output_path_for_page(page),
            "category": page["category"],
            "sources": page["source_files"],
        }

    def _render_bases_index(self, payload: Dict[str, Any], _site: WikiSiteDTO) -> List[str]:
        lines = []
        for family in payload.get("families", []):
            lines.extend([f"== {self._text(family.get('name'))} ==", self._text(family.get("summary")), ""])
            rows = [
                [
                    item.get("name", ""),
                    item.get("type", ""),
                    item.get("tier", ""),
                    item.get("level_req", ""),
                    item.get("sockets", ""),
                    item.get("speed_label", ""),
                ]
                for item in family.get("members", [])
            ]
            lines.extend(self._table(["Item", "Type", "Tier", "Req Lvl", "Sockets", "Speed"], rows))
            lines.append("")
        return lines

    def _render_misc_index(self, payload: Dict[str, Any], _site: WikiSiteDTO) -> List[str]:
        return self._render_misc_groups(payload.get("groups", []))

    def _render_gems_runes_index(self, payload: Dict[str, Any], _site: WikiSiteDTO) -> List[str]:
        return self._render_misc_groups(payload.get("groups", []))

    def _render_misc_groups(self, groups: List[Dict[str, Any]]) -> List[str]:
        lines = []
        for group in groups:
            lines.extend([f"== {self._text(group.get('category'))} ==", self._text(group.get("summary")), ""])
            rows = []
            for item in group.get("members", []):
                stack = f"Max {item.get('max_stack')}" if item.get("stackable") else ""
                rows.append([item.get("name", ""), item.get("code", ""), item.get("level", ""), item.get("level_req", ""), stack, item.get("description", "")])
            lines.extend(self._table(["Item", "Code", "Level", "Req Lvl", "Stack", "Description"], rows))
            lines.append("")
        return lines

    def _render_recipes_crafting(self, payload: Dict[str, Any], _site: WikiSiteDTO) -> List[str]:
        return self._render_recipe_sections(payload.get("page", {}).get("sections", []))

    def _render_recipes_corruptions(self, payload: Dict[str, Any], _site: WikiSiteDTO) -> List[str]:
        page = payload.get("page", {})
        lines = []
        for title, key in (
            ("Shared Corruptions", "combined_summaries"),
            ("Standard of Heroes", "standard_summaries"),
            ("The Divine Standard", "divine_summaries"),
        ):
            summaries = page.get(key, [])
            if not summaries:
                continue
            lines.extend([f"== {title} ==", ""])
            rows = []
            for summary in summaries:
                outcomes = "; ".join(
                    " ".join(str(outcome.get(part, "")).strip() for part in ("chance", "label", "detail", "range")).strip()
                    for outcome in summary.get("outcomes", [])
                )
                rows.append([summary.get("title", ""), " + ".join(summary.get("inputs", [])), outcomes])
            lines.extend(self._table(["Recipe", "Inputs", "Outcomes"], rows))
            lines.append("")
        return lines

    def _render_recipes_pierce(self, payload: Dict[str, Any], _site: WikiSiteDTO) -> List[str]:
        page = payload.get("page", {})
        lines = []
        rows = [
            [row.get("family", ""), row.get("property", ""), " + ".join(row.get("ingredients", [])), row.get("result", ""), ", ".join(row.get("item_types", []))]
            for row in page.get("families", [])
        ]
        lines.extend(self._table(["Family", "Property", "Ingredients", "Result", "Item Types"], rows))
        return lines

    def _render_recipes_reforge_upgrade(self, payload: Dict[str, Any], _site: WikiSiteDTO) -> List[str]:
        return self._render_recipe_sections(payload.get("page", {}).get("sections", []))

    def _render_recipes_materials(self, payload: Dict[str, Any], _site: WikiSiteDTO) -> List[str]:
        return self._render_recipe_sections(payload.get("page", {}).get("sections", []))

    def _render_recipes_all(self, payload: Dict[str, Any], _site: WikiSiteDTO) -> List[str]:
        page = payload.get("page", {})
        rows = [
            [row.get("system", ""), row.get("category", ""), row.get("recipe", ""), " + ".join(row.get("ingredients", [])), ", ".join(row.get("results", []))]
            for row in page.get("rows", [])
        ]
        return self._table(["System", "Category", "Recipe", "Ingredients", "Results"], rows)

    def _render_recipes_raw(self, payload: Dict[str, Any], _site: WikiSiteDTO) -> List[str]:
        page = payload.get("page", {})
        rows = [[row.get("id", ""), row.get("status", ""), row.get("description", ""), " + ".join(row.get("inputs", [])), ", ".join(row.get("outputs", []))] for row in page.get("rows", [])]
        return self._table(["ID", "Status", "Description", "Inputs", "Outputs"], rows)

    def _render_items_index(self, _payload: Dict[str, Any], site: WikiSiteDTO) -> List[str]:
        family_defs = (("unique", "Uniques"), ("set", "Sets"), ("runeword", "Runewords"))
        family_pages = []
        for family, label in family_defs:
            pages = [
                page
                for page in site["pages"]
                if page["kind"] == "item"
                and page["category"] == family
                and isinstance(page["payload"].get("page"), dict)
            ]
            if family == "set":
                pages.extend(self._set_item_pages(site))
            if not pages:
                continue
            family_pages.append((label, sorted(pages, key=lambda row: self.page_title(row).lower())))

        lines = ["== All Items ==", "__TOC__", ""]
        for label, pages in family_pages:
            lines.append(f"* [[#{label}|{label}]] ({len(pages)})")
        lines.append("")

        for label, pages in family_pages:
            lines.extend([f"=== {label} ===", ""])
            for page in sorted(pages, key=lambda row: self.page_title(row).lower()):
                lines.extend([f"== {self._text(self.page_title(page))} ==", *self._item_compare_table(page["payload"].get("page", {})), ""])
        return lines

    def _render_recipe_sections(self, sections: List[Dict[str, Any]]) -> List[str]:
        lines = []
        for section in sections:
            lines.extend([f"== {self._text(section.get('title'))} ==", self._text(section.get("summary")), ""])
            rows = []
            for row in section.get("rows", []):
                variants = row.get("variants")
                if variants:
                    for variant in variants:
                        rows.append([
                            row.get("item_type", ""),
                            variant.get("variant", ""),
                            " + ".join(variant.get("ingredients", [])),
                            "; ".join(variant.get("fixed_properties", [])),
                            variant.get("output", ""),
                        ])
                else:
                    rows.append([
                        row.get("description", row.get("recipe", "")),
                        " + ".join(row.get("ingredients", [])),
                        ", ".join(row.get("results", [])),
                        "; ".join(row.get("details", [])),
                    ])
            headers = ["Item Type", "Variant", "Ingredients", "Fixed Properties", "Result"] if rows and len(rows[0]) == 5 else ["Recipe", "Ingredients", "Results", "Details"]
            lines.extend(self._table(headers, rows))
            lines.append("")
        return lines

    def _render_item(self, payload: Dict[str, Any], _site: WikiSiteDTO) -> List[str]:
        page = payload.get("page", {})
        lines = [self._text(page.get("summary")), "", *self._item_compare_table(page)]
        rune_properties = page.get("rune_properties", [])
        if rune_properties:
            lines.extend(["", "== Rune Properties =="])
            for rune in rune_properties:
                lines.append(f"=== {self._text(rune.get('rune'))} ===")
                lines.extend(f"* {self._text(prop.get('text'))}" for prop in rune.get("properties", []))
        return lines

    def _render_runewords_index(self, payload: Dict[str, Any], _site: WikiSiteDTO) -> List[str]:
        rows = []
        for runeword in payload.get("runewords", []):
            rows.append([
                runeword.get("title", ""),
                ", ".join(runeword.get("base_items", [])),
                " + ".join(rune.get("name", "") for rune in runeword.get("runes", [])),
                "; ".join(runeword.get("properties", [])),
                runeword.get("status", ""),
            ])
        return self._table(["Runeword", "Bases", "Runes", "Properties", "Status"], rows)

    def _render_sets_index(self, payload: Dict[str, Any], _site: WikiSiteDTO) -> List[str]:
        lines = []
        for set_family in payload.get("sets", []):
            lines.extend([f"== {self._text(set_family.get('name'))} ==", self._text(set_family.get("summary")), ""])
            member_rows = [[member.get("display_name", ""), member.get("base_item", ""), member.get("item_type", ""), member.get("lvl_req", "")] for member in set_family.get("members", [])]
            lines.extend(self._table(["Item", "Base", "Type", "Req Lvl"], member_rows))
            bonus_rows = [
                {"cells": [bonus.get("label", ""), bonus.get("old", ""), bonus.get("new", "")], "status": bonus.get("status", "")}
                for bonus in set_family.get("set_bonuses", [])
            ]
            if bonus_rows:
                lines.extend(["", "=== Set Bonuses ===", *self._table(["Bonus", "Old", "New"], bonus_rows)])
            lines.append("")
        return lines

    def _set_item_pages(self, site: WikiSiteDTO) -> List[WikiPageDTO]:
        sets_page = next((page for page in site["pages"] if page["kind"] == "sets_index"), None)
        if not sets_page:
            return []
        result: List[WikiPageDTO] = []
        for set_family in sets_page["payload"].get("sets", []):
            for member in set_family.get("members", []):
                title = member.get("display_name", "Unknown")
                properties = [
                    {"text": str(prop.get("resolved_text", ""))}
                    for prop in member.get("properties", [])
                    if str(prop.get("resolved_text", "")).strip()
                ]
                comparison = member.get("comparison", {})
                page_payload = {
                    "title": title,
                    "summary": f"{title} from {set_family.get('name', 'Unknown Set')}.",
                    "stats": [
                        {"label": "Base Item", "value": member.get("base_item", "")},
                        {"label": "Item Type", "value": member.get("item_type", "")},
                        {"label": "Level Requirement", "value": member.get("lvl_req", "")},
                        {"label": "Set", "value": set_family.get("name", "")},
                    ],
                    "properties": properties,
                    "comparison": comparison,
                    "set_bonuses": set_family.get("set_bonuses", []),
                }
                result.append({
                    "kind": "item",
                    "title": str(title),
                    "output_path": "",
                    "template_name": "item.html",
                    "category": "set",
                    "source_files": [],
                    "payload": {"page": page_payload},
                })
        return result

    def _item_compare_table(self, page: Dict[str, Any]) -> List[str]:
        title = self._text(page.get("title", "Unknown"))
        comparison = page.get("comparison", {})
        rows = ['{| class="wikitable" ', '|- valign="top"', '! Retail !! BK']

        old_card, new_card, card_status = self._item_summary_cards(title, page, comparison)
        rows.extend(self._compare_row(old_card, new_card, card_status))

        prop_rows = comparison.get("property_rows", [])
        if prop_rows:
            rows.extend(['|- valign="top"', '|colspan="2"|', '<b>Properties</b><br />'])
            for row in prop_rows:
                rows.extend(self._compare_row(self._line_or_blank(row.get("old", "")), self._line_or_blank(row.get("new", "")), row.get("status", "")))
        else:
            properties = page.get("properties", [])
            if properties:
                prop_block = self._bullet_block(prop.get("text", "") for prop in properties)
                rows.extend(['|- valign="top"', '|colspan="2"|', '<b>Properties</b><br />'])
                rows.extend(self._compare_row("", prop_block, "added" if comparison.get("state") == "added" else "same"))

        set_bonus_rows = page.get("set_bonuses", [])
        if set_bonus_rows:
            rows.extend(['|- valign="top"', '|colspan="2"|', '<b>Set Bonuses</b><br />'])
            for row in set_bonus_rows:
                rows.extend(self._compare_row(self._line_or_blank(row.get("old", "")), self._line_or_blank(row.get("new", "")), row.get("status", "")))

        rows.append("|}")
        return rows

    def _item_summary_cards(self, title: str, page: Dict[str, Any], comparison: Dict[str, Any]) -> tuple[str, str, str]:
        identity = self._identity_compare_row(title, page, comparison)
        stats_old, stats_new, stats_status = self._stats_compare_blocks(page, comparison)
        old_parts = [part for part in (identity["old"], stats_old) if part]
        new_parts = [part for part in (identity["new"], stats_new) if part]
        return "".join(old_parts), "".join(new_parts), self._dominant_status([identity["status"], stats_status])

    def _identity_compare_row(self, title: str, page: Dict[str, Any], comparison: Dict[str, Any]) -> Dict[str, str]:
        base_row = self._comparison_stat_row(comparison, "Base Item") or self._comparison_stat_row(comparison, "Base")
        old_base = self._text(base_row.get("old", "") if base_row else "")
        new_base = self._text(base_row.get("new", "") if base_row else self._stat_value(page, "Base Item") or self._stat_value(page, "Base"))
        status = self._status_from_values(old_base, new_base, base_row.get("status", "") if base_row else "")
        return {
            "old": f"<b> {title} </b><br />Base Type: {old_base}<br />" if old_base else "",
            "new": f"<b> {title} </b><br />Base Type: {new_base}<br />" if new_base else f"<b> {title} </b><br />",
            "status": status,
        }

    def _stats_compare_blocks(self, page: Dict[str, Any], comparison: Dict[str, Any]) -> tuple[str, str, str]:
        old_lines = ["<b>Stats</b>"]
        new_lines = ["<b>Stats</b>"]
        statuses = []
        for stat in page.get("stats", []):
            label = str(stat.get("label", "")).strip()
            if label in {"Base Item", "Base", "Runes"}:
                continue
            compare_row = self._comparison_stat_row(comparison, label)
            old_value = self._text(compare_row.get("old", "") if compare_row else "")
            new_value = self._text(compare_row.get("new", "") if compare_row else stat.get("value", ""))
            if old_value:
                old_lines.append(f"{label}: {old_value}")
            if new_value:
                new_lines.append(f"{label}: {new_value}")
            statuses.append(self._status_from_values(old_value, new_value, compare_row.get("status", "") if compare_row else ""))
        old_block = "<br />".join(old_lines) + "<br />" if len(old_lines) > 1 else ""
        new_block = "<br />".join(new_lines) + "<br />" if len(new_lines) > 1 else ""
        return old_block, new_block, self._dominant_status(statuses)

    def _comparison_stat_row(self, comparison: Dict[str, Any], label: str) -> Dict[str, Any]:
        return next((row for row in comparison.get("stat_rows", []) if row.get("label") == label), {})

    def _stat_value(self, page: Dict[str, Any], label: str) -> str:
        row = next((stat for stat in page.get("stats", []) if stat.get("label") == label), {})
        return self._text(row.get("value", ""))

    def _compare_row(self, old: str, new: str, status: str) -> List[str]:
        return [f'|- valign="top"{self._row_attributes(status)}', f"| {old} || {new}"]

    def _line_or_blank(self, value: Any) -> str:
        text = self._text(value)
        return f"* {text}<br />" if text else ""

    def _bullet_block(self, values: Any) -> str:
        return "".join(self._line_or_blank(value) for value in values if self._text(value))

    def _status_from_values(self, old: str, new: str, status: str) -> str:
        if status:
            return status
        if old and new and old != new:
            return "changed"
        if new and not old:
            return "added"
        if old and not new:
            return "removed"
        return "same"

    def _dominant_status(self, statuses: List[str]) -> str:
        normalized = [status for status in statuses if status and status not in {"same", "unchanged"}]
        for candidate in ("changed", "modified", "added", "removed"):
            if candidate in normalized:
                return candidate
        return "same"

    def _render_bestiary_index(self, payload: Dict[str, Any], _site: WikiSiteDTO) -> List[str]:
        lines = []
        for group in payload.get("groups", []):
            lines.extend([f"== {self._text(group.get('act'))} ==", ""])
            rows = [[monster.get("name", ""), monster.get("level_hell", ""), ", ".join(monster.get("immunities_hell", [])), monster.get("status", "")] for monster in group.get("monsters", [])]
            lines.extend(self._table(["Monster", "Hell Level", "Hell Immunities", "Status"], rows))
            lines.append("")
        return lines

    def _render_drops_index(self, payload: Dict[str, Any], _site: WikiSiteDTO) -> List[str]:
        rows = []
        for group in payload.get("groups", []):
            candidates = "; ".join(f"{candidate.get('name')} ({candidate.get('chance_display')})" for candidate in group.get("candidates", []))
            rows.append([group.get("base_name", ""), group.get("quality_label", ""), group.get("total_weight", ""), candidates])
        return self._table(["Base", "Quality", "Total Weight", "Candidates"], rows)

    def _render_class(self, payload: Dict[str, Any], _site: WikiSiteDTO) -> List[str]:
        page = payload.get("page", {})
        lines = []
        for skill in page.get("skills", []):
            lines.extend([f"== {self._text(skill.get('name'))} ==", ""])
            rows = [[effect.get("effect", ""), effect.get("scaling", ""), effect.get("l1", ""), effect.get("l10", ""), effect.get("l20", ""), effect.get("l20_soft10", ""), effect.get("limit", "")] for effect in skill.get("effects", [])]
            lines.extend(self._table(["Effect", "Scaling", "L1", "L10", "L20", "L20+10", "Limit"], rows))
            if skill.get("synergies"):
                lines.extend(["", "=== Synergies ===", *[f"* '''{self._text(syn.get('name'))}''': {self._text(syn.get('effect'))}" for syn in skill.get("synergies", [])]])
            lines.append("")
        return lines

    def _render_generic(self, payload: Dict[str, Any]) -> List[str]:
        lines = []
        for key, value in payload.items():
            if isinstance(value, (str, int, float)):
                lines.append(f"* '''{self._text(key)}''': {self._text(value)}")
        return lines or ["''No structured MediaWiki renderer is defined for this page yet.''"]

    def _table(self, headers: List[str], rows: List[Any]) -> List[str]:
        if not rows:
            return ["''No entries.''"]
        lines = ['{| class="wikitable"', "|-"]
        lines.append("! " + " !! ".join(self._cell(header) for header in headers))
        for row in rows:
            status = ""
            cells = row
            if isinstance(row, dict):
                status = str(row.get("status", ""))
                cells = row.get("cells", [])
            lines.extend([f"|-{self._row_attributes(status)}", "| " + " || ".join(self._cell(value) for value in cells)])
        lines.append("|}")
        return lines

    def _row_attributes(self, status: str) -> str:
        normalized = status.strip().lower()
        if normalized in {"same", "unchanged"}:
            return ""
        styles = {
            "added": "color:#2b6f47; font-weight:600;",
            "changed": "color:#8a5a00; font-weight:600;",
            "modified": "color:#8a5a00; font-weight:600;",
            "removed": "color:#7a7168;",
        }
        style = styles.get(normalized)
        if not style:
            return ""
        class_name = "is-changed" if normalized == "modified" else f"is-{normalized}"
        return f' class="wiki-diff-row {class_name}" style="{style}"'

    def _text(self, value: Any) -> str:
        if value is None:
            return ""
        return str(value).replace("\r", " ").replace("\n", " ").strip()

    def _cell(self, value: Any) -> str:
        return self._text(value).replace("|", "{{!}}")


class MediaWikiPublisher:
    def __init__(self, output_dir: str, renderer: MediaWikiRenderer | None = None):
        self.output_dir = output_dir
        self.renderer = renderer or MediaWikiRenderer()

    def publish(self, site: WikiSiteDTO) -> None:
        os.makedirs(self.output_dir, exist_ok=True)
        manifest = []
        generated_paths = set()

        for page in site["pages"]:
            if not self.renderer.should_publish_page(page):
                continue
            relative_path = self.renderer.output_path_for_page(page)
            full_path = os.path.join(self.output_dir, relative_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(self.renderer.render_page(page, site))
            generated_paths.add(relative_path.replace("\\", "/"))
            manifest.append(self.renderer.manifest_entry(page))

        manifest_path = os.path.join(self.output_dir, "manifest.json")
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)
        generated_paths.add("manifest.json")

        self._remove_stale_files(generated_paths)

    def _remove_stale_files(self, generated_paths: set[str]) -> None:
        for root, dirs, files in os.walk(self.output_dir, topdown=False):
            for filename in files:
                full_path = os.path.join(root, filename)
                rel_path = os.path.relpath(full_path, self.output_dir).replace("\\", "/")
                if rel_path in generated_paths:
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
