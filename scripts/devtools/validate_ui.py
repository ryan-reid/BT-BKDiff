import json
import os
import sys
import re
from legacy.extract_class_skills_paginated import D2Data, Evaluator, SYNERGY_MAP

def normalize_val(val):
    if not val or val == "" or val == "NOT_SHOWN": return None
    val = val.replace('%', '').strip()
    # Handle ranges
    if '-' in val:
        # Check if it's a negative number vs a range
        # A range has a '-' that is not at the start, or multiple '-'
        parts = val.split('-')
        if val.startswith('-'):
            # Potentially -15 or -40--10
            if len(parts) == 2: # Just a negative number like -15
                return float(val)
            elif len(parts) == 3: # Negative range like -40--10 -> ['', '40', '', '10']? No, split('-') on '-40--10' is ['', '40', '', '10']
                # Better use regex to find all numbers including negative ones
                nums = re.findall(r'-?\d+\.?\d*', val)
                if len(nums) == 2: return [float(nums[0]), float(nums[1])]
                return float(nums[0]) if nums else None
        else:
            if len(parts) == 2:
                return [float(parts[0]), float(parts[1])]
    
    # Fallback to regex for any complex strings
    nums = re.findall(r'-?\d+\.?\d*', val)
    if len(nums) == 2: return [float(nums[0]), float(nums[1])]
    return float(nums[0]) if nums else None

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Assuming script is in BT-BKDiff/scripts
    # root should be BT-BKDiff
    root = os.path.dirname(script_dir)
    
    mod_path = os.path.join(root, "mods/BKDiablo/bkdiablo.mpq")
    retail_path = os.path.join(os.path.dirname(root), "data/retail") # E:\Games\GeminiDiff\data\retail
    if not os.path.exists(retail_path):
        retail_path = os.path.join(root, "data/retail")
    
    data = D2Data(mod_path, retail_path)
    ev = Evaluator(data)
    
    test_path = os.path.join(root, "tests/amazon_test_cases.json")
    with open(test_path, 'r') as f:
        tc = json.load(f)

    results = []
    
    for group_name, skills in tc['groups'].items():
        print(f"\n>>> Testing Group: {group_name}")
        for sk_name, sk_data in skills.items():
            print(f"  Skill: {sk_name}")
            
            # Setup Synergies
            SYNERGY_MAP.clear()
            for syn_n, syn_v in sk_data.get('synergies', {}).items():
                SYNERGY_MAP[syn_n.lower().replace(' ', '')] = syn_v
            
            skill_obj = data.skill_map.get(sk_name.lower())
            if not skill_obj:
                print(f"    ERROR: Skill '{sk_name}' not found in data.")
                continue
            
            desc_row = data.desc_map.get(skill_obj['skilldesc'].lower())
            if not desc_row:
                print(f"    ERROR: SkillDesc '{skill_obj['skilldesc']}' not found.")
                continue
            
            for scen in sk_data['scenarios']:
                lvl = scen['lvl']
                blvl = scen['blvl']
                ui = scen['ui']
                
                print(f"    Scenario: L{lvl} (Base {blvl})")
                
                for i in range(1, 10):
                    line_id = desc_row.get(f"descline{i}")
                    if not line_id or line_id == '0': continue
                    
                    text_raw = data.strings.get(desc_row.get(f"desctexta{i}", "").lower(), "")
                    label = text_raw.replace('%d', '').replace('%+d', '').replace('%%', '%').strip(': ')
                    
                    ui_key = None
                    # Prioritize exact match
                    for k in ui.keys():
                        if k.lower() == label.lower():
                            ui_key = k
                            break
                    
                    # Then partial match
                    if not ui_key:
                        for k in ui.keys():
                            if k.lower() in label.lower() or label.lower() in k.lower():
                                ui_key = k
                                break
                    
                    if ui_key:
                        expected_raw = str(ui[ui_key])
                        if expected_raw == "" or expected_raw == "NOT_SHOWN": continue
                        
                        expected = None
                        calculated_str = "N/A"
                        try:
                            expected = normalize_val(expected_raw)
                            calculated_str = ev.calculate(skill_obj, desc_row, i, lvl, blvl)
                            calculated = normalize_val(calculated_str)
                            
                            match = False
                            if expected is None or calculated is None:
                                match = (expected == calculated)
                            elif isinstance(expected, list) and isinstance(calculated, list):
                                match = abs(expected[0] - calculated[0]) < 1.1 and abs(expected[1] - calculated[1]) < 1.1
                            elif not isinstance(expected, list) and not isinstance(calculated, list):
                                match = abs(expected - calculated) < 1.1
                            
                            if not match:
                                print(f"      [FAIL] {ui_key}: UI={expected_raw}, Calc={calculated_str} (Label: {label})")
                                results.append({"skill": sk_name, "scenario": f"L{lvl}", "field": ui_key, "ui": expected_raw, "calc": calculated_str})
                        except Exception as e:
                            print(f"      [ERROR] {ui_key}: {e} (Expected: {expected_raw}, Calc: {calculated_str})")

    print("\n" + "="*40)
    if not results:
        print("ALL TESTS PASSED!")
    else:
        print(f"FOUND {len(results)} DISCREPANCIES:")
        for r in results:
            print(f"  {r['skill']} ({r['scenario']}) - {r['field']}: UI={r['ui']} vs Calc={r['calc']}")

if __name__ == "__main__":
    main()
