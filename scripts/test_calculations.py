import unittest
import json
import os
import re
import sys
from extract_class_skills_paginated import D2Data, Evaluator, SYNERGY_MAP

def normalize_val(val):
    if not val or val == "" or val == "NOT_SHOWN": return None
    val = str(val).replace('%', '').strip()
    # Handle ranges
    if '-' in val:
        # Check if it's a negative number vs a range
        if val.startswith('-'):
            parts = val.split('-')
            if len(parts) == 2: # Just a negative number like -15
                return float(val)
            else:
                # Negative range like -40--10 or similar
                nums = re.findall(r'-?\d+\.?\d*', val)
                if len(nums) == 2: return [float(nums[0]), float(nums[1])]
                return float(nums[0]) if nums else None
        else:
            parts = val.split('-')
            if len(parts) == 2:
                return [float(parts[0]), float(parts[1])]
    
    # Fallback to regex for any complex strings
    nums = re.findall(r'-?\d+\.?\d*', val)
    if len(nums) == 2: return [float(nums[0]), float(nums[1])]
    return float(nums[0]) if nums else None

class TestD2Calculations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        root = os.path.dirname(script_dir)
        
        mod_path = os.path.join(root, "mods/BKDiablo/bkdiablo.mpq")
        retail_path = os.path.join(os.path.dirname(root), "data/retail")
        if not os.path.exists(retail_path):
            retail_path = os.path.join(root, "data/retail")
        
        cls.data = D2Data(mod_path, retail_path)
        cls.ev = Evaluator(cls.data)
        
        test_path = os.path.join(root, "tests/amazon_test_cases.json")
        with open(test_path, 'r') as f:
            cls.test_cases = json.load(f)

    def test_all_skills(self):
        """Data-driven test for all skills in the JSON test cases."""
        for group_name, skills in self.test_cases['groups'].items():
            for sk_name, sk_data in skills.items():
                # Setup Synergies for this skill
                SYNERGY_MAP.clear()
                for syn_n, syn_v in sk_data.get('synergies', {}).items():
                    SYNERGY_MAP[syn_n.lower().replace(' ', '')] = syn_v
                
                skill_obj = self.data.skill_map.get(sk_name.lower())
                self.assertIsNotNone(skill_obj, f"Skill '{sk_name}' not found in data.")
                
                desc_row = self.data.desc_map.get(skill_obj['skilldesc'].lower())
                self.assertIsNotNone(desc_row, f"SkillDesc '{skill_obj['skilldesc']}' not found.")
                
                for scen in sk_data['scenarios']:
                    lvl = scen['lvl']
                    blvl = scen['blvl']
                    ui = scen['ui']
                    
                    # For each UI field, find matching description line
                    for ui_key, expected_raw in ui.items():
                        print(f"      TESTING: {sk_name} {ui_key}")
                        if expected_raw == "" or expected_raw == "NOT_SHOWN":
                            continue

                        expected = normalize_val(expected_raw)
                        if expected is None: continue

                        # Find which line in skilldesc matches this UI key
                        best_match = None # (block, i, label, calc_str)
                        found_line = False
                        
                        for block in ["", "dsc2", "dsc3"]:
                            for i in range(1, 10):
                                prefix = f"{block}line" if block else "descline"
                                line_id = desc_row.get(f"{prefix}{i}")
                                if not line_id or line_id == '0': continue
                                
                                text_prefix = f"{block}texta" if block else "desctexta"
                                text_raw = self.data.strings.get(desc_row.get(f"{text_prefix}{i}", "").lower(), "")
                                label = text_raw.replace('%d', '').replace('%+d', '').replace('%%', '%').strip(': ')
                                if label.startswith('%s:'): continue
                                
                                def clean(s):
                                    s = s.lower().replace('x', '').replace(':', '').replace('%', '').replace('+', '').replace('-', ' ')
                                    s = s.replace('duration', '').replace('length', '').replace('of ', '').replace('freezes', 'freeze').replace('attacks', 'attack')
                                    s = re.sub(r'\s+', ' ', s).strip()
                                    return s
                                
                                clean_ui = clean(ui_key)
                                clean_label = clean(label)
                                
                                match = False
                                if clean_ui == clean_label:
                                    match = True
                                elif clean_ui in clean_label or clean_label in clean_ui:
                                    if len(clean_ui) >= 4 or clean_ui in ["life"]:
                                        if ui_key.lower() == "damage" and "converts" in label.lower():
                                            match = False
                                        else:
                                            match = True
                                
                                if match:
                                    # Check type compatibility before committing to this match
                                    calc_str = self.ev.calculate(skill_obj, desc_row, i, lvl, blvl, block=block)
                                    calc_val = normalize_val(calc_str)
                                    if calc_val is not None:
                                        # compatible if both are lists or both are not lists
                                        if isinstance(expected, list) == isinstance(calc_val, list):
                                            if best_match is None or len(clean_label) > len(clean(best_match[2])):
                                                best_match = (block, i, label, calc_str, calc_val)
                        
                        if best_match:
                            block, i, label, calculated_str, calculated = best_match
                            found_line = True
                            
                            if isinstance(expected, list) and isinstance(calculated, list):
                                val_delta = 5.0 if expected[0] > 1000 else 1.1
                                self.assertAlmostEqual(expected[0], calculated[0], delta=val_delta, 
                                                     msg=f"{sk_name} L{lvl} {ui_key} MIN: UI={expected[0]} Calc={calculated[0]} (Label: {label})")
                                self.assertAlmostEqual(expected[1], calculated[1], delta=val_delta, 
                                                     msg=f"{sk_name} L{lvl} {ui_key} MAX: UI={expected[1]} Calc={calculated[1]} (Label: {label})")
                            elif not isinstance(expected, list) and not isinstance(calculated, list):
                                val_delta = 5.0 if expected > 1000 else 1.1
                                self.assertAlmostEqual(expected, calculated, delta=val_delta, 
                                                     msg=f"{sk_name} L{lvl} {ui_key}: UI={expected} Calc={calculated} (Label: {label})")
                                    
                        if not found_line:
                            self.fail(f"Could not find display line for UI field '{ui_key}' in skill '{sk_name}'")

if __name__ == '__main__':
    unittest.main()
