import json
import os
import re
import sys
from difflib import SequenceMatcher


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRIPT_DIR = os.path.join(ROOT, "scripts")
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from d2_repository import D2Repository
from d2_services import SkillAnalyzerService


def normalize_skill_key(name: str) -> str:
    return re.sub(r"[\s']", "", name.strip().lower())


def normalize_val(val):
    if val is None:
        return None
    text = str(val).strip()
    if not text or text in {"NOT_SHOWN", "N/A", "TRUE"}:
        return None
    text = text.replace("%", "").strip()

    if "-" in text:
        if text.startswith("-"):
            nums = re.findall(r"-?(?:\d+\.?\d*|\.\d+)", text)
            if len(nums) == 1:
                return float(nums[0])
            if len(nums) >= 2:
                return [float(nums[0]), float(nums[1])]
        else:
            nums = re.findall(r"-?(?:\d+\.?\d*|\.\d+)", text)
            if len(nums) >= 2:
                return [float(nums[0]), float(nums[1])]

    nums = re.findall(r"-?(?:\d+\.?\d*|\.\d+)", text)
    if len(nums) >= 2:
        return [float(nums[0]), float(nums[1])]
    return float(nums[0]) if nums else None


def clean_label(text: str) -> str:
    value = text.lower()
    value = value.replace("%", "")
    value = value.replace("+", "")
    value = value.replace("-", " ")
    value = value.replace("x", "")
    value = value.replace("to", " to ")
    value = value.replace("per second", "")
    value = value.replace("seconds", "")
    value = value.replace("second", "")
    value = value.replace("mana cost", "mana")
    value = re.sub(r"\s+", " ", value).strip(" :")
    return value


def match_effect_value(effects, expected_key):
    expected_clean = clean_label(expected_key)
    best_match = None
    best_score = 0.0

    for effect in effects:
        label_clean = clean_label(effect["label"])
        score = 0.0
        if label_clean == expected_clean:
            score = 1.0
        else:
            score = SequenceMatcher(None, expected_clean, label_clean).ratio()
            if expected_clean in label_clean or label_clean in expected_clean:
                score = max(score, 0.75)

        if score > best_score:
            best_score = score
            best_match = effect["value"]

    return best_match if best_score >= 0.75 else None


def diff_score(expected_raw, actual_raw):
    if actual_raw is None:
        return 1e9

    expected = normalize_val(expected_raw)
    actual = normalize_val(actual_raw)
    if expected is None:
        return 0.0
    if actual is None:
        return 1e9

    if isinstance(expected, list) and isinstance(actual, list):
        return abs(expected[0] - actual[0]) + abs(expected[1] - actual[1])
    if not isinstance(expected, list) and not isinstance(actual, list):
        return abs(expected - actual)
    return 1e9


def summarize_candidate(ui_expectations, effects):
    field_rows = []
    total = 0.0
    matched = 0
    for ui_key, expected_raw in ui_expectations:
        actual_raw = match_effect_value(effects, ui_key)
        score = diff_score(expected_raw, actual_raw)
        if score < 1e9:
            matched += 1
            total += score
        field_rows.append(
            {
                "field": ui_key,
                "expected": expected_raw,
                "actual": actual_raw,
                "score": score,
            }
        )
    return {
        "total_score": total + ((len(ui_expectations) - matched) * 1000000.0),
        "matched_fields": matched,
        "field_rows": field_rows,
    }


def main():
    repo = D2Repository(os.path.join(ROOT, "mods", "BKDiablo", "bkdiablo.mpq"))
    service = SkillAnalyzerService(repo)

    with open(os.path.join(ROOT, "tests", "druid_test_cases.template.json"), "r", encoding="utf-8") as f:
        expectations = json.load(f)

    skill_name_map = {}
    for skill in service.generate_skill_tree("dru")["skills"]:
        display_name = skill["name"]
        internal_name = skill.get("raw_row", {}).get("skill", display_name)
        skill_name_map[display_name] = internal_name

    def render_skill_effects(skill_name, lvl, blvl, synergies):
        internal_name = skill_name_map.get(skill_name, skill_name)
        scenario_levels = {
            normalize_skill_key(skill_name): blvl,
            normalize_skill_key(internal_name): blvl,
        }
        for name, level in synergies.items():
            if level is None:
                continue
            scenario_levels[normalize_skill_key(name)] = int(level)
            internal_syn_name = skill_name_map.get(name)
            if internal_syn_name:
                scenario_levels[normalize_skill_key(internal_syn_name)] = int(level)
        return service.get_skill_display_effects(internal_name, lvl, blvl, scenario_levels)

    sweep_detail = {}
    scenario_analysis = []

    for group_name, skills in expectations["groups"].items():
        sweep_detail[group_name] = {}
        for skill_name, skill_data in skills.items():
            sweep_detail[group_name][skill_name] = {"with_synergies": [], "without_synergies": []}

            for mode_name, synergies in [
                ("with_synergies", skill_data.get("synergies", {})),
                ("without_synergies", {}),
            ]:
                for lvl in range(1, 41):
                    blvl = min(lvl, 20)
                    effects = render_skill_effects(skill_name, lvl, blvl, synergies)
                    sweep_detail[group_name][skill_name][mode_name].append(
                        {
                            "lvl": lvl,
                            "blvl": blvl,
                            "effects": effects,
                        }
                    )

            for scenario in skill_data["scenarios"]:
                ui_expectations = [(k, v) for k, v in scenario["ui"].items() if v not in ["", "NOT_SHOWN", "N/A", "TRUE"]]
                best_with = None
                best_without = None

                for lvl in range(1, 41):
                    blvl = min(lvl, 20)

                    with_effects = render_skill_effects(skill_name, lvl, blvl, skill_data.get("synergies", {}))
                    with_summary = summarize_candidate(ui_expectations, with_effects)
                    candidate_with = {
                        "lvl": lvl,
                        "blvl": blvl,
                        "matched_fields": with_summary["matched_fields"],
                        "total_score": with_summary["total_score"],
                        "field_rows": with_summary["field_rows"],
                    }
                    if best_with is None or (
                        candidate_with["matched_fields"] > best_with["matched_fields"]
                        or (
                            candidate_with["matched_fields"] == best_with["matched_fields"]
                            and candidate_with["total_score"] < best_with["total_score"]
                        )
                    ):
                        best_with = candidate_with

                    without_effects = render_skill_effects(skill_name, lvl, blvl, {})
                    without_summary = summarize_candidate(ui_expectations, without_effects)
                    candidate_without = {
                        "lvl": lvl,
                        "blvl": blvl,
                        "matched_fields": without_summary["matched_fields"],
                        "total_score": without_summary["total_score"],
                        "field_rows": without_summary["field_rows"],
                    }
                    if best_without is None or (
                        candidate_without["matched_fields"] > best_without["matched_fields"]
                        or (
                            candidate_without["matched_fields"] == best_without["matched_fields"]
                            and candidate_without["total_score"] < best_without["total_score"]
                        )
                    ):
                        best_without = candidate_without

                scenario_analysis.append(
                    {
                        "group": group_name,
                        "skill": skill_name,
                        "scenario": {
                            "lvl": int(scenario["lvl"]),
                            "blvl": int(scenario["blvl"]),
                        },
                        "synergies": skill_data.get("synergies", {}),
                        "best_with_synergies": best_with,
                        "best_without_synergies": best_without,
                    }
                )

    output_dir = os.path.join(ROOT, "output")
    os.makedirs(output_dir, exist_ok=True)

    json_path = os.path.join(output_dir, "druid_level_sweep_debug.json")
    with open(json_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(
            {
                "scenario_analysis": scenario_analysis,
                "sweep_detail": sweep_detail,
            },
            f,
            indent=2,
        )

    lines = []
    lines.append("# Druid Level Sweep Debug Report")
    lines.append("")
    lines.append("Sweep range: `L1-L40` with `blvl = min(level, 20)`.")
    lines.append("Each scenario is evaluated twice: with the fixture synergies and with synergies disabled.")
    lines.append("")
    lines.append("## Scenario Summary")
    lines.append("")
    lines.append("| Group | Skill | Scenario | Best With Synergies | Score | Best Without Synergies | Score |")
    lines.append("|---|---|---|---|---:|---|---:|")

    for entry in scenario_analysis:
        s = entry["scenario"]
        bw = entry["best_with_synergies"]
        bn = entry["best_without_synergies"]
        lines.append(
            f"| {entry['group']} | {entry['skill']} | L{s['lvl']}/{s['blvl']} | "
            f"L{bw['lvl']}/{bw['blvl']} ({bw['matched_fields']} fields) | {bw['total_score']:.2f} | "
            f"L{bn['lvl']}/{bn['blvl']} ({bn['matched_fields']} fields) | {bn['total_score']:.2f} |"
        )

    for entry in scenario_analysis:
        s = entry["scenario"]
        lines.append("")
        lines.append(f"## {entry['skill']} L{s['lvl']}/{s['blvl']}")
        lines.append("")
        if entry["synergies"]:
            lines.append(f"Fixture synergies: `{entry['synergies']}`")
            lines.append("")

        for title, candidate in [
            ("Best With Synergies", entry["best_with_synergies"]),
            ("Best Without Synergies", entry["best_without_synergies"]),
        ]:
            lines.append(f"### {title}")
            lines.append("")
            lines.append(f"Best level: `L{candidate['lvl']}/{candidate['blvl']}`")
            lines.append(f"Matched fields: `{candidate['matched_fields']}`")
            lines.append(f"Total score: `{candidate['total_score']:.2f}`")
            lines.append("")
            lines.append("| Field | Expected | Actual | Score |")
            lines.append("|---|---:|---:|---:|")
            for row in candidate["field_rows"]:
                actual = row["actual"] if row["actual"] is not None else "NO MATCH"
                score = "NO MATCH" if row["score"] >= 1e9 else f"{row['score']:.2f}"
                lines.append(f"| {row['field']} | {row['expected']} | {actual} | {score} |")
            lines.append("")

    md_path = os.path.join(output_dir, "druid_level_sweep_debug.md")
    with open(md_path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")

    print(json_path)
    print(md_path)


if __name__ == "__main__":
    main()
