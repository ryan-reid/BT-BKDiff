import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from cli.generate_wiki import add_comparison_links

class TestComparisonSwitch(unittest.TestCase):
    def test_nested_pages_and_missing_counterparts(self):
        def site(paths): return {'pages': [{'output_path': p, 'payload': {}} for p in paths]}
        retail = site(['index.html','items/example/index.html','mercenaries/removed/index.html'])
        bt = site(['index.html','items/example/index.html'])
        add_comparison_links(retail, bt)
        self.assertEqual(retail['pages'][1]['payload']['comparison_switch']['bt'], '../../compare-bt/items/example/index.html')
        self.assertEqual(bt['pages'][1]['payload']['comparison_switch']['retail'], '../../../items/example/index.html')
        self.assertEqual(retail['pages'][2]['payload']['comparison_switch']['bt'], '../../compare-bt/index.html')
        self.assertEqual(bt['pages'][0]['payload']['comparison_switch']['active'], 'bt')
