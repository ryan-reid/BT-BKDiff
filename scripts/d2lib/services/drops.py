from __future__ import annotations

from typing import Any, Dict, List, Set, Tuple

from d2lib.repository import D2RepositoryProtocol


MONSTER_TC_FIELDS = [
    ("TreasureClass(H)", "Hell"),
    ("TreasureClassChamp(H)", "Hell Champion"),
    ("TreasureClassUnique(H)", "Hell Unique"),
    ("TreasureClassQuest(H)", "Hell Quest"),
    ("TreasureClassDesecrated(H)", "Hell Desecrated"),
    ("TreasureClassDesecratedChamp(H)", "Hell Desecrated Champion"),
    ("TreasureClassDesecratedUnique(H)", "Hell Desecrated Unique"),
    ("TreasureClassHerald(H)", "Hell Herald"),
]

SUPERUNIQUE_TC_FIELDS = [
    ("TC(H)", "Hell"),
    ("TC(H) Desecrated", "Hell Desecrated"),
]


class DropSourceAnalyzerService:
    def __init__(self, repo: D2RepositoryProtocol):
        self.repo = repo

    def analyze_drop_sources(self) -> Dict[str, Any]:
        treasure_classes = self.repo.get_excel_table("treasureclassex")
        tc_names = {
            str(row.get("Treasure Class", "")).strip()
            for row in treasure_classes
            if str(row.get("Treasure Class", "")).strip()
        }
        item_lookup = self._item_lookup()

        rows: List[Dict[str, Any]] = []
        by_name: Dict[str, Dict[str, Any]] = {}
        parent_links: Dict[str, List[Dict[str, str]]] = {}

        for raw_row in treasure_classes:
            name = str(raw_row.get("Treasure Class", "")).strip()
            if not name:
                continue
            entries = self._entries(raw_row, tc_names, item_lookup)
            row = {
                "name": name,
                "group": str(raw_row.get("group", "")).strip(),
                "level": str(raw_row.get("level", "")).strip(),
                "picks": str(raw_row.get("Picks", "")).strip(),
                "no_drop": str(raw_row.get("NoDrop", "")).strip(),
                "quality_weights": self._quality_weights(raw_row),
                "entries": entries,
                "parents": [],
                "monster_sources": [],
                "superunique_sources": [],
                "sources": [],
            }
            rows.append(row)
            by_name[name] = row

            for entry in entries:
                if entry["kind"] != "treasure_class":
                    continue
                parent_links.setdefault(entry["code"], []).append(
                    {"name": name, "prob": entry["prob"], "kind": "parent"}
                )

        for child_name, parents in parent_links.items():
            child = by_name.get(child_name)
            if child is not None:
                child["parents"] = sorted(parents, key=lambda source: source["name"].lower())

        self._add_monster_sources(by_name)
        self._add_superunique_sources(by_name)

        for row in rows:
            row["sources"] = self._combined_sources(row)
            row["search_text"] = self._search_text(row)

        rows = sorted(rows, key=lambda row: row["name"].lower())
        summary = {
            "total_treasure_classes": len(rows),
            "direct_item_refs": sum(1 for row in rows for entry in row["entries"] if entry["kind"] == "item"),
            "nested_tc_refs": sum(1 for row in rows for entry in row["entries"] if entry["kind"] == "treasure_class"),
            "monster_source_refs": sum(len(row["monster_sources"]) for row in rows),
            "superunique_source_refs": sum(len(row["superunique_sources"]) for row in rows),
        }
        return {"summary": summary, "rows": rows}

    def _item_lookup(self) -> Dict[str, Dict[str, str]]:
        lookup: Dict[str, Dict[str, str]] = {}
        for table_name, source_label in (
            ("weapons", "Weapon"),
            ("armor", "Armor"),
            ("misc", "Misc"),
        ):
            for row in self.repo.get_excel_table(table_name):
                code = str(row.get("code", "")).strip()
                if not code:
                    continue
                name_key = str(row.get("namestr", "") or row.get("name", "")).strip()
                display_name = self.repo.get_string(name_key) or name_key or code
                lookup[code] = {
                    "code": code,
                    "label": display_name,
                    "source": source_label,
                    "type": str(row.get("type", "")).strip(),
                }
        return lookup

    def _entries(
        self,
        row: Dict[str, str],
        tc_names: Set[str],
        item_lookup: Dict[str, Dict[str, str]],
    ) -> List[Dict[str, str]]:
        entries: List[Dict[str, str]] = []
        for index in range(1, 11):
            raw = str(row.get(f"Item{index}", "")).strip()
            if not raw:
                continue
            code, modifiers = self._split_entry(raw)
            prob = str(row.get(f"Prob{index}", "")).strip()
            kind, label, source = self._classify_entry(code, tc_names, item_lookup)
            entries.append(
                {
                    "slot": str(index),
                    "raw": raw,
                    "code": code,
                    "kind": kind,
                    "label": label,
                    "prob": prob,
                    "modifiers": modifiers,
                    "source": source,
                }
            )
        return entries

    def _classify_entry(
        self,
        code: str,
        tc_names: Set[str],
        item_lookup: Dict[str, Dict[str, str]],
    ) -> Tuple[str, str, str]:
        if code in tc_names:
            return "treasure_class", code, "Treasure Class"
        item = item_lookup.get(code)
        if item is not None:
            return "item", item["label"], item["source"]
        return "token", code, "Drop Token"

    @staticmethod
    def _split_entry(raw: str) -> Tuple[str, str]:
        if "," not in raw:
            return raw.strip(), ""
        code, modifiers = raw.split(",", 1)
        return code.strip(), modifiers.strip()

    @staticmethod
    def _quality_weights(row: Dict[str, str]) -> List[Dict[str, str]]:
        weights: List[Dict[str, str]] = []
        for field in ("Unique", "Set", "Rare", "Magic"):
            value = str(row.get(field, "")).strip()
            if value and value != "0":
                weights.append({"label": field, "value": value})
        return weights

    def _add_monster_sources(self, by_name: Dict[str, Dict[str, Any]]) -> None:
        for monster in self.repo.get_excel_table("monstats"):
            monster_id = str(monster.get("Id", "")).strip()
            name_key = str(monster.get("NameStr", "")).strip()
            monster_name = self.repo.get_string(name_key) or name_key or monster_id
            for field, label in MONSTER_TC_FIELDS:
                tc_name = str(monster.get(field, "")).strip()
                if not tc_name:
                    continue
                row = by_name.get(tc_name)
                if row is None:
                    continue
                row["monster_sources"].append(
                    {
                        "name": monster_name,
                        "id": monster_id,
                        "field": field,
                        "label": label,
                        "kind": "monster",
                    }
                )

    def _add_superunique_sources(self, by_name: Dict[str, Dict[str, Any]]) -> None:
        for superunique in self.repo.get_excel_table("superuniques"):
            raw_name = str(
                superunique.get("Name", "")
                or superunique.get("Superunique", "")
                or superunique.get("Class", "")
            ).strip()
            source_name = self.repo.get_string(raw_name) or raw_name
            for field, label in SUPERUNIQUE_TC_FIELDS:
                tc_name = str(superunique.get(field, "")).strip()
                if not tc_name:
                    continue
                row = by_name.get(tc_name)
                if row is None:
                    continue
                row["superunique_sources"].append(
                    {
                        "name": source_name,
                        "field": field,
                        "label": label,
                        "kind": "superunique",
                    }
                )

    @staticmethod
    def _combined_sources(row: Dict[str, Any]) -> List[Dict[str, str]]:
        sources: List[Dict[str, str]] = []
        sources.extend(
            {
                "name": parent["name"],
                "label": f"Nested parent, weight {parent['prob']}" if parent.get("prob") else "Nested parent",
                "kind": "parent",
            }
            for parent in row["parents"]
        )
        sources.extend(
            {
                "name": source["name"],
                "label": source["label"],
                "kind": "monster",
            }
            for source in sorted(row["monster_sources"], key=lambda source: source["name"].lower())
        )
        sources.extend(
            {
                "name": source["name"],
                "label": source["label"],
                "kind": "superunique",
            }
            for source in sorted(row["superunique_sources"], key=lambda source: source["name"].lower())
        )
        return sources

    @staticmethod
    def _search_text(row: Dict[str, Any]) -> str:
        parts = [
            row["name"],
            row.get("group", ""),
            row.get("level", ""),
            " ".join(entry["label"] for entry in row["entries"]),
            " ".join(entry["code"] for entry in row["entries"]),
            " ".join(source["name"] for source in row["sources"]),
        ]
        return " ".join(part for part in parts if part).strip()
