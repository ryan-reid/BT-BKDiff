import csv
import json
import os
import re
import sys
from typing import Dict, List, Set, Tuple


SCRIPT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO_ROOT = os.path.dirname(SCRIPT_ROOT)
if SCRIPT_ROOT not in sys.path:
    sys.path.insert(0, SCRIPT_ROOT)

from d2_repository import D2Repository


csv.field_size_limit(1000000)

TEST_CASES_PATH = os.path.join(REPO_ROOT, "tests", "amazon_test_cases.json")
SOURCE_MOD_PATH = os.path.join(REPO_ROOT, "mods", "BKDiablo", "bkdiablo.mpq")
FIXTURE_ROOT = os.path.join(REPO_ROOT, "tests", "fixtures", "amazon_skill_snapshot")
FIXTURE_MOD_PATH = os.path.join(FIXTURE_ROOT, "mod")

SKILL_REF_PATTERNS = [
    re.compile(r"skill\('([^']+)'\.", re.IGNORECASE),
    re.compile(r"sklvl\('([^']+)'\.", re.IGNORECASE),
]
MISSILE_REF_PATTERN = re.compile(r"miss\('([^']+)'\.", re.IGNORECASE)


def normalize_skill_key(name: str) -> str:
    return re.sub(r"[\s']", "", name.strip().lower())


def load_tsv_with_lines(file_path: str) -> Tuple[List[str], List[Dict[str, str]], Dict[str, int]]:
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = [line.rstrip("\n\r") for line in f if line.rstrip("\n\r")]

    if lines and lines[0].startswith("\ufeff"):
        lines[0] = lines[0][1:]

    headers = [header.strip() for header in lines[0].split("\t")]
    rows: List[Dict[str, str]] = []
    line_numbers: Dict[str, int] = {}
    reader = csv.DictReader(lines, delimiter="\t", quoting=csv.QUOTE_NONE)
    for index, row in enumerate(reader, start=2):
        clean_row = {(str(k).strip() if k else str(k)): (str(v).strip() if v else "") for k, v in row.items()}
        rows.append(clean_row)
        key = clean_row.get("skill") or clean_row.get("skilldesc") or clean_row.get("Missile")
        if key:
            line_numbers[key.strip().lower()] = index
    return headers, rows, line_numbers


def write_tsv(file_path: str, headers: List[str], rows: List[Dict[str, str]]) -> None:
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8", newline="") as f:
        f.write("\t".join(headers) + "\n")
        for row in rows:
            values = [str(row.get(header, "")).replace("\r", " ").replace("\n", " ") for header in headers]
            f.write("\t".join(values) + "\n")


def extract_referenced_skills(values: List[str]) -> Set[str]:
    referenced: Set[str] = set()
    for value in values:
        for pattern in SKILL_REF_PATTERNS:
            for match in pattern.findall(value or ""):
                referenced.add(match.strip().lower())
    return referenced


def extract_referenced_missiles(values: List[str]) -> Set[str]:
    referenced: Set[str] = set()
    for value in values:
        for match in MISSILE_REF_PATTERN.findall(value or ""):
            referenced.add(match.strip().lower())
    return referenced


def main() -> None:
    with open(TEST_CASES_PATH, "r", encoding="utf-8") as f:
        cases = json.load(f)

    repo = D2Repository(SOURCE_MOD_PATH)

    skills_path = os.path.join(SOURCE_MOD_PATH, "data", "global", "excel", "skills.txt")
    skilldesc_path = os.path.join(SOURCE_MOD_PATH, "data", "global", "excel", "skilldesc.txt")
    missiles_path = os.path.join(SOURCE_MOD_PATH, "data", "global", "excel", "missiles.txt")

    skills_headers, skills_rows, skill_lines = load_tsv_with_lines(skills_path)
    skilldesc_headers, skilldesc_rows, skilldesc_lines = load_tsv_with_lines(skilldesc_path)
    missiles_headers, missiles_rows, missile_lines = load_tsv_with_lines(missiles_path)

    skills_map = {row.get("skill", "").strip().lower(): row for row in skills_rows if row.get("skill")}
    skilldesc_map = {row.get("skilldesc", "").strip().lower(): row for row in skilldesc_rows if row.get("skilldesc")}
    missiles_map = {row.get("Missile", "").strip().lower(): row for row in missiles_rows if row.get("Missile")}

    selected_skills: Set[str] = set()
    for group in cases["groups"].values():
        for skill_name, skill_data in group.items():
            selected_skills.add(skill_name.strip().lower())
            for synergy_name in skill_data.get("synergies", {}):
                selected_skills.add(synergy_name.strip().lower())

    queue = list(selected_skills)
    selected_desc: Set[str] = set()
    selected_missiles: Set[str] = set()

    while queue:
        skill_name = queue.pop()
        skill_row = skills_map.get(skill_name)
        if not skill_row:
            continue

        desc_name = skill_row.get("skilldesc", "").strip().lower()
        if desc_name:
            selected_desc.add(desc_name)

        etype = skill_row.get("EType", "").strip().lower()
        if etype:
            mastery_name = f"passive_{etype}_mastery"
            if mastery_name in skills_map and mastery_name not in selected_skills:
                selected_skills.add(mastery_name)
                queue.append(mastery_name)

        referenced_skills = extract_referenced_skills(list(skill_row.values()))
        for referenced_skill in referenced_skills:
            if referenced_skill in skills_map and referenced_skill not in selected_skills:
                selected_skills.add(referenced_skill)
                queue.append(referenced_skill)

    for desc_name in list(selected_desc):
        desc_row = skilldesc_map.get(desc_name)
        if not desc_row:
            continue

        for field in ["descmissile1", "descmissile2", "descmissile3"]:
            missile_name = desc_row.get(field, "").strip().lower()
            if missile_name and missile_name in missiles_map:
                selected_missiles.add(missile_name)

        referenced_skills = extract_referenced_skills(list(desc_row.values()))
        for referenced_skill in referenced_skills:
            if referenced_skill in skills_map and referenced_skill not in selected_skills:
                selected_skills.add(referenced_skill)
                queue.append(referenced_skill)

        referenced_missiles = extract_referenced_missiles(list(desc_row.values()))
        for missile_name in referenced_missiles:
            if missile_name in missiles_map:
                selected_missiles.add(missile_name)

    filtered_skills = [row for row in skills_rows if row.get("skill", "").strip().lower() in selected_skills]
    filtered_desc = [row for row in skilldesc_rows if row.get("skilldesc", "").strip().lower() in selected_desc]
    filtered_missiles = [row for row in missiles_rows if row.get("Missile", "").strip().lower() in selected_missiles]

    string_keys: Set[str] = set()
    for skill_row in filtered_skills:
        if skill_row.get("skill"):
            string_keys.add(skill_row["skill"].strip().lower())

    for desc_row in filtered_desc:
        for field in [
            "str name",
            "str short",
            "str long",
            "desctexta1", "desctexta2", "desctexta3", "desctexta4", "desctexta5", "desctexta6", "desctexta7", "desctexta8", "desctexta9",
            "desctextb1", "desctextb2", "desctextb3", "desctextb4", "desctextb5", "desctextb6", "desctextb7", "desctextb8", "desctextb9",
            "dsc2texta1", "dsc2texta2", "dsc2texta3", "dsc2texta4", "dsc2texta5", "dsc2texta6", "dsc2texta7", "dsc2texta8", "dsc2texta9",
            "dsc2textb1", "dsc2textb2", "dsc2textb3", "dsc2textb4", "dsc2textb5", "dsc2textb6", "dsc2textb7", "dsc2textb8", "dsc2textb9",
            "dsc3texta1", "dsc3texta2", "dsc3texta3", "dsc3texta4", "dsc3texta5", "dsc3texta6", "dsc3texta7", "dsc3texta8", "dsc3texta9",
            "dsc3textb1", "dsc3textb2", "dsc3textb3", "dsc3textb4", "dsc3textb5", "dsc3textb6", "dsc3textb7", "dsc3textb8", "dsc3textb9",
        ]:
            value = desc_row.get(field, "").strip().lower()
            if value:
                string_keys.add(value)

    snapshot_strings = []
    for key in sorted(string_keys):
        snapshot_strings.append({"Key": key, "enUS": repo.get_string(key)})

    write_tsv(os.path.join(FIXTURE_MOD_PATH, "data", "global", "excel", "skills.txt"), skills_headers, filtered_skills)
    write_tsv(os.path.join(FIXTURE_MOD_PATH, "data", "global", "excel", "skilldesc.txt"), skilldesc_headers, filtered_desc)
    write_tsv(os.path.join(FIXTURE_MOD_PATH, "data", "global", "excel", "missiles.txt"), missiles_headers, filtered_missiles)

    strings_dir = os.path.join(FIXTURE_MOD_PATH, "data", "local", "lng", "strings")
    os.makedirs(strings_dir, exist_ok=True)
    with open(os.path.join(strings_dir, "skills_snapshot.json"), "w", encoding="utf-8") as f:
        json.dump(snapshot_strings, f, indent=2)

    manifest = {
        "source_mod_path": SOURCE_MOD_PATH,
        "test_cases_path": TEST_CASES_PATH,
        "tables": {
            "skills": {
                "source_file": skills_path,
                "row_count": len(filtered_skills),
                "source_lines": {name: skill_lines[name] for name in sorted(selected_skills) if name in skill_lines},
            },
            "skilldesc": {
                "source_file": skilldesc_path,
                "row_count": len(filtered_desc),
                "source_lines": {name: skilldesc_lines[name] for name in sorted(selected_desc) if name in skilldesc_lines},
            },
            "missiles": {
                "source_file": missiles_path,
                "row_count": len(filtered_missiles),
                "source_lines": {name: missile_lines[name] for name in sorted(selected_missiles) if name in missile_lines},
            },
        },
        "strings": {
            "output_file": os.path.join(strings_dir, "skills_snapshot.json"),
            "key_count": len(snapshot_strings),
            "keys": sorted(string_keys),
        },
    }

    os.makedirs(FIXTURE_ROOT, exist_ok=True)
    with open(os.path.join(FIXTURE_ROOT, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"Wrote Amazon snapshot fixture to {FIXTURE_ROOT}")
    print(f"skills={len(filtered_skills)} skilldesc={len(filtered_desc)} missiles={len(filtered_missiles)} strings={len(snapshot_strings)}")


if __name__ == "__main__":
    main()
