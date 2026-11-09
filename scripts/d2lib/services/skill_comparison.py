"""Evidence-first skill cards. No tooltip arithmetic or guessed game results.

Join each version independently before comparing: a mod can replace a missile,
description, state, or summon rather than editing the original record.
"""
from __future__ import annotations

import re
from collections import deque

from d2lib.utils import slugify


CLASSES = {"ama": "Amazon", "sor": "Sorceress", "nec": "Necromancer",
           "pal": "Paladin", "bar": "Barbarian", "dru": "Druid",
           "ass": "Assassin", "war": "Warlock"}
TABLE_KEYS = {"skills": "skill", "skilldesc": "skilldesc", "missiles": "Missile",
              "states": "state", "itemstatcost": "Stat", "monstats": "Id",
              "monstats2": "Id", "monprop": "Id", "pettype": "pet type",
              "properties": "code", "itemtypes": "Code"}
SKILL_REF = re.compile(r"\b(?:skill|sklvl)\('([^']+)'\.", re.I)
STAT_REF = re.compile(r"\bstat\('([^']+)'\.", re.I)
MISSILE_REF = re.compile(r"\bmiss\('([^']+)'\.", re.I)
PARAM_REF = re.compile(r"\bpar(\d+)\b", re.I)
TOOLTIP_NUMBER = re.compile(r"%\+?d")
BASE_FIELDS = (
    ("reqlevel", "Required character level"),
    ("maxlvl", "Maximum hard points"),
    ("reqskill1", "Prerequisite 1"),
    ("reqskill2", "Prerequisite 2"),
    ("reqskill3", "Prerequisite 3"),
    ("mana", "Base mana (source value)"),
    ("minmana", "Minimum mana"),
    ("manashift", "Mana shift"),
    ("EType", "Skill damage element"),
    ("MinDam", "Base physical damage minimum (source value)"),
    ("MaxDam", "Base physical damage maximum (source value)"),
    ("EMin", "Base elemental damage minimum (source value)"),
    ("EMax", "Base elemental damage maximum (source value)"),
    ("HitShift", "Damage shift"),
    ("summon", "Summoned creature"),
)


def comparison_row(label, before, after):
    return {"label": label, "old": before, "new": after,
            "status": "unchanged" if before == after else "changed"}


def skill_description(snapshot, root):
    skill = snapshot["records"].get("skills:" + root, {}).get("row", {})
    desc = snapshot["records"].get("skilldesc:" + value(skill, "skilldesc").lower(), {}).get("row", {})
    return skill, desc


def synergy_entries(snapshot, root, repo):
    skill, desc = skill_description(snapshot, root)
    entries = {}
    for block in ("dsc2", "dsc3"):
        in_synergies = False
        for index in range(1, 8):
            effect_key = value(desc, f"{block}texta{index}")
            if effect_key.lower() == "sksyn":
                in_synergies = True
                continue
            kind = value(desc, f"{block}line{index}")
            if not in_synergies or kind not in {"18", "76", "77", "79"}:
                continue
            skill_key = effect_key if kind == "18" else value(desc, f"{block}textb{index}")
            if not skill_key:
                continue
            inputs = [value(desc, f"{block}calc{part}{index}") for part in ("a", "b")]
            resolved = []
            for raw in filter(None, inputs):
                parameter = PARAM_REF.fullmatch(raw)
                resolved.append((value(skill, "Param" + parameter[1]) or raw) if parameter else raw)
            effect = re.sub(r"^%s\s*:?\s*", "", repo.get_string(effect_key))
            slots = TOOLTIP_NUMBER.findall(effect)
            if kind == "18":
                effect = "Listed in tooltip"
            elif kind in {"76", "77"} and len(slots) == len(resolved) and all(re.fullmatch(r"[+-]?\d+", n) for n in resolved):
                numbers = iter(resolved)
                effect = TOOLTIP_NUMBER.sub(lambda match: match[0] % int(next(numbers)), effect).replace("%%", "%")
            elif resolved:
                effect = f"{effect.replace('%%', '%')} · Source inputs: {', '.join(resolved)}"
            key = (skill_key.lower(), effect_key.lower() if kind != "18" else "")
            entries[key] = (repo.get_string(skill_key), effect)
    return entries


def value(row, field):
    return str((row or {}).get(field, "") or "").strip()


def group_for(table, field):
    f = field.lower()
    if table == "strings" or table == "skilldesc":
        return "Tooltip & presentation"
    if "func" in f:
        return "Engine functions"
    if f.startswith(("shitpar", "chitpar", "dparam")):
        return "Damage & hit behavior"
    if "calc" in f or f.startswith(("param", "cltparam")):
        return "Formulas & parameters"
    if any(s in f for s in ("dam", "hit", "elen", "elev", "emin", "emax")) or f == "etype":
        return "Damage & hit behavior"
    if any(s in f for s in ("mana", "delay", "req", "maxlvl")):
        return "Requirements & costs"
    if any(s in f for s in ("missile", "state", "stat", "summon", "pet", "skill")):
        return "Linked behavior"
    return "Other settings"


def row_diff(old, new):
    result = []
    for field in dict.fromkeys(list(old or {}) + list(new or {})):
        if field.startswith("*") or field == "None":
            continue  # Author comments are annotations, not executable changes.
        before, after = value(old, field), value(new, field)
        if not before and not after:
            continue
        result.append({"label": field, "old": before, "new": after,
                       "status": "unchanged" if before == after else "changed"})
    return result


def parameter_note(row, field):
    normalized = re.sub(r"[^a-z0-9]", "", field.lower())
    for key, text in (row or {}).items():
        if key.startswith("*") and re.match(re.escape(normalized) + r"(?:description|desc)",
                                             re.sub(r"[^a-z0-9]", "", key.lower())):
            return str(text or "")
    return ""


class SkillSource:
    def __init__(self, repo):
        self.repo = repo
        self.tables = {}
        self.aliases = {}
        self.sources = {}
        for table, key in TABLE_KEYS.items():
            rows = repo.get_excel_table(table)
            self.tables[table] = {value(r, key).lower(): r for r in rows if value(r, key)}
            self.aliases[table] = {value(r, f).lower(): value(r, key).lower()
                                   for r in rows for f in ("*Id", "*ID", "Id", "ID")
                                   if value(r, f) and value(r, key)}
            path = getattr(repo, "excel_sources", {}).get(table, "")
            self.sources[table] = path.replace("\\", "/")

    def lookup(self, table, key):
        key = str(key).strip().lower()
        if key not in self.tables[table]:
            key = self.aliases[table].get(key, key)
        return key, self.tables[table].get(key)

    def snapshot(self, root):
        records, edges, references, missing = {}, [], [], []
        queue = deque([("skills", root, "", "root")])
        while queue:
            table, requested, parent, field = queue.popleft()
            key, row = self.lookup(table, requested)
            record_id = table + ":" + key
            if parent:
                edges.append({"from": parent, "field": field, "to": record_id})
            if row is None:
                if parent:
                    missing.append(f"{parent} → {field} → {record_id}")
                continue
            if record_id in records:
                continue
            records[record_id] = {"table": table, "key": key, "row": row,
                                  "source": self.sources[table]}

            def add(target, name, via):
                if str(name).strip():
                    queue.append((target, name, record_id, via))

            def localized(text, via):
                resolved = self.repo.get_string(text) if text.lower() in self.repo.strings else ""
                if resolved:
                    string_id = "strings:" + text.lower()
                    records[string_id] = {"table": "strings", "key": text,
                                          "row": {"enUS": resolved}, "source": "Resolved localization: " + text}
                    edges.append({"from": record_id, "field": via, "to": string_id})
                else:
                    missing.append(f"{record_id} → {via} → strings:{text}")

            def skill_reference(name, via):
                _, ref = self.lookup("skills", name)
                cc = value(ref, "charclass")
                references.append({"name": value(ref, "skill") or name, "field": via,
                                   "from": record_id,
                                   "href": f"classes/{slugify(CLASSES[cc])}/#{slugify(value(ref, 'skill'))}" if cc in CLASSES else ""})

            for f, raw in row.items():
                text = str(raw or "").strip()
                if not text or f.startswith("*"):
                    continue
                lower = f.lower()
                if table == "skills":
                    if lower == "skilldesc": add("skilldesc", text, f)
                    elif re.fullmatch(r"(?:srv|clt)missile[a-d]?", lower): add("missiles", text, f)
                    elif lower in {"aurastate", "auratargetstate", "passivestate", "state1", "state2", "state3"}: add("states", text, f)
                    elif re.fullmatch(r"(?:aura|passive)stat\d+", lower): add("itemstatcost", text, f)
                    elif lower == "summon": add("monstats", text, f)
                    elif lower in {"pettype", "requirespettype"}: add("pettype", text, f)
                    elif re.fullmatch(r"sumskill\d+", lower): add("skills", text, f)
                    elif re.fullmatch(r"reqskill\d+", lower): skill_reference(text, f)
                    elif re.fullmatch(r"(?:[ie]type[ab]\d+|passiveitype)", lower): add("itemtypes", text, f)
                elif table == "skilldesc":
                    if lower.startswith("descmissile"): add("missiles", text, f)
                    if lower.startswith("str ") or "text" in lower:
                        localized(text, f)
                elif table == "missiles":
                    if re.fullmatch(r"(?:(?:clt)?(?:hit)?submissile\d+|explosionmissile)", lower): add("missiles", text, f)
                    # Skill is a damage-source reference, not another emitted missile.
                    if lower == "skill": skill_reference(text, f)
                elif table == "states":
                    if lower == "stat": add("itemstatcost", text, f)
                    if lower == "missile": add("missiles", text, f)
                    if lower == "skill": skill_reference(text, f)
                elif table == "monstats":
                    if lower in {"namestr", "descstr"}: localized(text, f)
                    if lower == "monstatsex": add("monstats2", text, f)
                    if lower == "monprop": add("monprop", text, f)
                    if re.fullmatch(r"skill\d+", lower): add("skills", text, f)
                    if re.fullmatch(r"miss(?:a[12]|s[1-4]|c|sq)", lower): add("missiles", text, f)
                elif table == "monprop":
                    if re.fullmatch(r"prop\d+(?:\([nh]\))?", lower): add("properties", text, f)
                elif table == "properties":
                    if re.fullmatch(r"stat\d+", lower): add("itemstatcost", text, f)
                elif table == "itemtypes":
                    if lower in {"equiv1", "equiv2"}: add("itemtypes", text, f)
                elif table == "itemstatcost":
                    if lower in {"op base", "op stat1", "op stat2", "op stat3", "maxstat"}: add("itemstatcost", text, f)
                    if lower in {"descstrpos", "descstrneg", "descstr2", "dgrpstrpos", "dgrpstrneg", "dgrpstr2"}: localized(text, f)
                for ref in SKILL_REF.findall(text):
                    if ref.lower() != root.lower(): skill_reference(ref, f)
                for ref in STAT_REF.findall(text): add("itemstatcost", ref, f)
                for ref in MISSILE_REF.findall(text): add("missiles", ref, f)
        return {"records": records, "edges": edges, "references": references,
                "missing": list(dict.fromkeys(missing))}


class SkillComparisonService:
    def __init__(self, current_repo, baseline_repo):
        self.current = SkillSource(current_repo)
        self.baseline = SkillSource(baseline_repo)

    @staticmethod
    def _facts(snapshot, root):
        facts = {}
        root_row = snapshot["records"].get("skills:" + root, {}).get("row", {})
        for field, label in BASE_FIELDS:
            raw = value(root_row, field)
            if raw:
                display = {"mag": "Magic", "fire": "Fire", "ltng": "Lightning", "cold": "Cold", "pois": "Poison", "phys": "Physical"}.get(raw, raw) if field == "EType" else raw
                facts[("skill", field)] = {"label": label, "value": display, "evidence": f"skills:{root} · {field}"}
        # These parameter meanings belong to this specific function pair.
        # Never apply them to arbitrary missile hit functions.
        for rid, record in snapshot["records"].items():
            row = record["row"]
            if record["table"] != "missiles" or value(row, "pSrvHitFunc") != "7" or value(row, "pSrvDmgFunc") != "15":
                continue
            target = {"0": "All enemy monster types", "1": "Undead", "2": "Demons", "3": "Demons and undead"}.get(value(row, "sHitPar2"))
            if target is not None:
                facts[(rid, "targets")] = {"label": f"{record['key']} · Full-damage targets", "value": target,
                                            "evidence": f"{rid} · pSrvHitFunc=7, pSrvDmgFunc=15, sHitPar2={value(row, 'sHitPar2')}"}
            healing = {"0": "Disabled", "1": "Enabled"}.get(value(row, "sHitPar1"))
            if healing is not None:
                facts[(rid, "healing")] = {"label": f"{record['key']} · Ally healing", "value": healing,
                                            "evidence": f"{rid} · pSrvHitFunc=7, sHitPar1={value(row, 'sHitPar1')}"}
        return facts

    def compare(self, key):
        old = self.baseline.snapshot(key)
        new = self.current.snapshot(key)
        source_row = new["records"].get("skills:" + key, old["records"].get("skills:" + key, {})).get("row", {})
        name = value(source_row, "skill")
        facts = []
        before, after = self._facts(old, key), self._facts(new, key)
        for identity in dict.fromkeys(list(after) + list(before)):
            a, b = before.get(identity, {}), after.get(identity, {})
            facts.append({"label": (b or a)["label"], "old": a.get("value", ""), "new": b.get("value", ""),
                          "status": "unchanged" if a.get("value") == b.get("value") else "changed",
                          "evidence": " | ".join(dict.fromkeys(x["evidence"] for x in (a, b) if x))})
        records = []
        for rid in dict.fromkeys(list(new["records"]) + list(old["records"])):
            a, b = old["records"].get(rid), new["records"].get(rid)
            r = b or a
            rows = row_diff(a["row"] if a else None, b["row"] if b else None)
            for row in rows:
                row["group"] = group_for(r["table"], row["label"])
                # Comments can explain a raw parameter, without turning it into a computed value.
                row["old_note"] = parameter_note(a["row"] if a else None, row["label"])
                row["new_note"] = parameter_note(b["row"] if b else None, row["label"])
            changed = sum(row["status"] == "changed" for row in rows)
            records.append({"id": rid, "table": r["table"], "key": r["key"], "rows": rows,
                            "changed": changed, "status": "added" if not a else "removed" if not b else "modified" if changed else "unchanged",
                            "old_source": a["source"] if a else "", "new_source": b["source"] if b else ""})
        root_old = old["records"].get("skills:" + key)
        root_new = new["records"].get("skills:" + key)
        status = "added" if not root_old else "removed" if not root_new else "modified" if any(r["status"] != "unchanged" for r in records) else "unchanged"
        warnings = []
        for side, snap in (("old", old), ("new", new)):
            if snap["missing"]:
                warnings.append({"side": side, "text": f"{len(snap['missing'])} unresolved source links; inspect linked records for details."})
            tooltip = " ".join(r["row"].get("enUS", "") for r in snap["records"].values() if r["table"] == "strings")
            disabled = any(f["value"] == "Disabled" for k, f in self._facts(snap, key).items() if k[1] == "healing")
            if disabled and re.search(r"heals? allies", tooltip, re.I):
                warnings.append({"side": side, "kind": "tooltip", "text": "Tooltip mentions ally healing, but a linked missile's server settings disable it."})
        refs = []
        for snap in (new, old):
            for ref in snap["references"]:
                if ref not in refs: refs.append(ref)
        formula_labels = {"EDmgSymPerCalc": "Elemental damage bonus formula", "DmgSymPerCalc": "Physical damage bonus formula",
                          "ELenSymPerCalc": "Duration bonus formula", "petmax": "Summon limit formula",
                          "aurarangecalc": "Aura range formula", "auralencalc": "Aura duration formula",
                          "ToHitCalc": "Attack rating formula", "localdelay": "Local casting delay",
                          "globaldelay": "Global casting delay"}
        formula_rows = []
        root_record = next((r for r in records if r["id"] == "skills:" + key), None)
        if root_record:
            for row in root_record["rows"]:
                if row["label"] in formula_labels or re.fullmatch(r"(?:(?:prg|passive|aurastat)?calc\d+|sumsk\d+calc)", row["label"]):
                    formula = dict(row, label=formula_labels.get(row["label"], row["label"]))
                    if formula["old_note"] != formula["new_note"]:
                        formula["status"] = "changed"
                    formula_rows.append(formula)
                    parameters = {}
                    for side, root in (("old", root_old), ("new", root_new)):
                        source = root["row"] if root else {}
                        for number in dict.fromkeys(PARAM_REF.findall(row[side])):
                            field = "Param" + number
                            raw = value(source, field)
                            if raw:
                                parameters.setdefault("par" + number, {})[side] = (raw, parameter_note(source, field))
                    for parameter_name, sides in parameters.items():
                        old_value, old_note = sides.get("old", ("", ""))
                        new_value, new_note = sides.get("new", ("", ""))
                        parameter = comparison_row(parameter_name, old_value, new_value)
                        formula_rows.append(dict(parameter, old_note=old_note, new_note=new_note))
        def tooltip(snap):
            _, desc = skill_description(snap, key)
            text_key = value(desc, "str long") or value(desc, "str short")
            return snap["records"].get("strings:" + text_key.lower(), {}).get("row", {}).get("enUS", "")
        old_text, new_text = tooltip(old), tooltip(new)
        tooltip_row = comparison_row("In-game description", old_text, new_text)
        before = synergy_entries(old, key, self.baseline.repo)
        after = synergy_entries(new, key, self.current.repo)
        synergy_rows = [
            comparison_row((after.get(identity) or before[identity])[0],
                           before.get(identity, ("", ""))[1], after.get(identity, ("", ""))[1])
            for identity in dict.fromkeys([*after, *before])
        ]
        visible_rows = [tooltip_row, *facts, *formula_rows, *synergy_rows]
        display_status = status if status in {"added", "removed"} else (
            "modified" if any(row["status"] == "changed" for row in visible_rows) else "unchanged"
        )
        text = " ".join([name, *(f"{r['label']} {r['old']} {r['new']}" for r in visible_rows)])
        return {"name": name, "slug": slugify(name), "status": status, "facts": facts,
                "display_status": display_status, "formula_rows": formula_rows, "tooltip": tooltip_row,
                "synergy_rows": synergy_rows,
                "records": records, "references": refs, "warnings": warnings,
                "old_edges": old["edges"], "new_edges": new["edges"],
                "old_missing": old["missing"], "new_missing": new["missing"],
                "changed_fields": sum(r["changed"] for r in records), "search_text": text}

    def class_pages(self):
        classes = {cc: [] for cc in CLASSES}
        keys = dict.fromkeys(list(self.current.tables["skills"]) + list(self.baseline.tables["skills"]))
        for key in keys:
            row = self.current.tables["skills"].get(key, self.baseline.tables["skills"].get(key))
            cc = value(row, "charclass")
            if cc in classes:
                classes[cc].append(self.compare(key))
        return [{"class_name": CLASSES[cc], "skills": skills,
                 "source_files": list(dict.fromkeys(p for source in (self.current, self.baseline)
                                                     for p in source.sources.values() if p))}
                for cc, skills in classes.items() if skills]
