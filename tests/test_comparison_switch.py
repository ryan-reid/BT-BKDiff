import sys
import unittest
import tempfile
from unittest.mock import patch
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from cli.generate_wiki import add_comparison_links, run

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

    def test_dual_build_uses_shared_reports_and_distinct_baselines(self):
        with tempfile.TemporaryDirectory() as directory:
            output = str(Path(directory) / 'wiki')
            with patch('cli.generate_wiki.WikiGenerator') as generator, \
                 patch('cli.generate_wiki.WikiPublisher') as publisher:
                generator.return_value.build_site.side_effect = [
                    {'pages': [{'output_path': 'index.html', 'payload': {}}]},
                    {'pages': [{'output_path': 'index.html', 'payload': {}}]},
                ]
                run('bk-items', 'skills', output, old_item_db_dir='retail-items',
                    retail_data_dir='retail-data', bt_item_db_dir=directory, bt_data_dir=directory)
                retail, bt = generator.call_args_list
                self.assertEqual(retail.args[2], output)
                self.assertEqual(bt.args[2], output)
                self.assertEqual(retail.kwargs['old_item_db_dir'], 'retail-items')
                self.assertEqual(bt.kwargs['old_item_db_dir'], directory)
                self.assertEqual(bt.kwargs['retail_data_dir'], directory)
                self.assertEqual(bt.kwargs['old_label'], 'BTDiablo')
                self.assertEqual([call.args[0] for call in publisher.call_args_list],
                                 [output, str(Path(output) / 'compare-bt')])
