"""Pre-resistance damage components from the skill table."""

import ast
import operator
import re

from d2lib.repository import normalize_d2_value


ELEMENTS = {"fire": "Fire", "ltng": "Lightning", "cold": "Cold", "frze": "Cold", "mag": "Magic", "phys": "Physical"}
SKILL_VALUE = re.compile(r"\bskill\('([^']+)'\.([a-z0-9]+)\)", re.I)
MAGIC_MASTERY = re.compile(r"\bstat\('passive_mag_mastery'\.accr\)", re.I)
LINEAR_PARAMETERS = {
    "ln12": (1, 2), "ln34": (3, 4), "ln56": (5, 6), "ln78": (7, 8),
    "ln91": (9, 10), "ln21": (11, 12), "ln43": (13, 14), "ln65": (15, 16),
    "ln87": (17, 18), "ln92": (19, 20),
}


def _divide(numerator, denominator):
    result = abs(numerator) // abs(denominator)
    return -result if (numerator < 0) != (denominator < 0) else result


def _evaluate(node, inputs):
    if isinstance(node, ast.Constant) and type(node.value) is int:
        return node.value
    if isinstance(node, ast.Name) and node.id in inputs:
        return inputs[node.id]
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
        result = _evaluate(node.operand, inputs)
        return -result if isinstance(node.op, ast.USub) else result
    if isinstance(node, ast.BinOp):
        operation = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: _divide}.get(type(node.op))
        if operation:
            return operation(_evaluate(node.left, inputs), _evaluate(node.right, inputs))
    if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
            and node.func.id in {"min", "max"} and len(node.args) == 2 and not node.keywords):
        operation = min if node.func.id == "min" else max
        return operation(*(_evaluate(arg, inputs) for arg in node.args))
    raise ValueError("Unsupported damage expression")


def _integer(row, field):
    return int(normalize_d2_value(row.get(field)) or 0)


def _formula_inputs(row, level):
    inputs = {"lvl": level, "blvl": level}
    parameters = {index: _integer(row, f"Param{index}") for index in range(1, 21)}
    for index, value in parameters.items():
        inputs[f"{'par' if index < 10 else 'pa'}{index}"] = value
    for symbol, (base, increment) in LINEAR_PARAMETERS.items():
        inputs[symbol] = parameters[base] + (level - 1) * parameters[increment] if level else 0
    return inputs


def _synergy(formula, row, skills, level, max_synergies):
    inputs = _formula_inputs(row, level)

    def skill_value(match):
        key = match[1].casefold()
        symbol = match[2].lower()
        if key == row["skill"].casefold():
            return str(inputs[symbol])
        other = skills.get(key, {})
        cap = _integer(other, "maxlvl")
        if cap < 1 or other.get("charclass") != row.get("charclass"):
            raise ValueError("Missing or unavailable synergy skill")
        return str(_formula_inputs(other, cap if max_synergies else 0)[symbol])

    formula = SKILL_VALUE.sub(skill_value, formula)
    # The preview has no gear or mastery investment.
    formula = MAGIC_MASTERY.sub("0", formula)
    return _evaluate(ast.parse(formula.lower(), mode="eval").body, inputs)


def _scaled(level, base, increments):
    previous = 1
    for boundary, increment in zip((8, 16, 22, 28, level), increments):
        base += max(0, min(level, boundary) - previous) * increment
        previous = boundary
    return base


def skill_damage_preview(skill, skills):
    """Build per-level values for the two synergy presets used by the static wiki."""
    if not skill:
        return None
    try:
        cap = _integer(skill, "maxlvl")
        shift = _integer(skill, "HitShift")
        if not 1 <= cap <= 99 or not 0 <= shift <= 8:
            return None
    except ValueError:
        return None

    components = []
    omitted = []
    for label, minimum, maximum, min_levels, max_levels, formula_field, elemental in (
        ("Physical", "MinDam", "MaxDam", "MinLevDam", "MaxLevDam", "DmgSymPerCalc", False),
        (ELEMENTS.get(skill.get("EType")), "EMin", "EMax", "EMinLev", "EMaxLev", "EDmgSymPerCalc", True),
    ):
        try:
            ranges = [
                (_integer(skill, field), [_integer(skill, f"{prefix}{i}") for i in range(1, 6)])
                for field, prefix in ((minimum, min_levels), (maximum, max_levels))
            ]
            if not any(base or any(increments) for base, increments in ranges):
                continue
            if not label or (not elemental and skill.get("kick") == "1"):
                raise ValueError("Damage requires a different calculation")
            formula = normalize_d2_value(skill.get(formula_field))
            presets = {}
            for preset, max_synergies in (("max", True), ("none", False)):
                results = []
                for level in range(1, cap + 1):
                    bonus = _synergy(formula, skill, skills, level, max_synergies) if formula else 0
                    values = []
                    for index, (base, increments) in enumerate(ranges):
                        damage = _scaled(level, base, increments)
                        if elemental:
                            damage <<= shift
                        if not elemental or index == 1 or damage > 256 or increments[0]:
                            damage += _divide(damage * bonus, 100)
                        if not elemental:
                            damage <<= shift
                        values.append(damage >> 8)
                    results.append(values)
                presets[preset] = results
            components.append({"label": label, "presets": presets})
        except (ValueError, SyntaxError, ArithmeticError, KeyError):
            omitted.append(label or {"pois": "Poison", "burn": "Burn"}.get(skill.get("EType"), "Elemental"))
    if not components and not omitted:
        return None
    return {"cap": cap, "components": components, "omitted": omitted}
