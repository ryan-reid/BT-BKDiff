import os
import argparse
import sys
import json
from typing import List, Dict, Optional
from d2_repository import D2Repository
from d2_services import PropertyResolverService, ItemAnalyzerService
from d2_exporters import MarkdownExporter, JsonExporter

class ExportOrchestrator:
    def __init__(self, repo: D2Repository, analyzer: ItemAnalyzerService, exporter: MarkdownExporter, json_exporter: JsonExporter):
        self.repo = repo
        self.analyzer = analyzer
        self.exporter = exporter
        self.json_exporter = json_exporter

    def get_group_for_category(self, category: str) -> str:
        cat_lower = category.lower()
        if any(w in cat_lower for w in ['axe', 'bow', 'club', 'crossbow', 'hammer', 'javelin', 'knife', 'mace', 'polearm', 'scepter', 'spear', 'staff', 'sword', 'throwing', 'wand', 'weapon']): return 'weapons'
        if any(h in cat_lower for h in ['helm', 'circlet', 'pelt', 'primal']): return 'helms'
        if any(s in cat_lower for s in ['shield', 'auric', 'voodoo']): return 'shields'
        if any(c in cat_lower for c in ['armor', 'tors']): return 'chests'
        if any(b in cat_lower for b in ['belt', 'boots', 'gloves']): return 'armor'
        if any(acc in cat_lower for acc in ['amulet', 'ring', 'charm', 'jewel']): return 'accessories'
        if any(cls in cat_lower for cls in ['amazon', 'auric', 'grimoire', 'hand to hand', 'orb', 'pelt', 'primal', 'voodoo']): return 'class_specific'
        return 'other'

    def run_export(self, output_dir: str, export_format: str):
        groups = ['weapons', 'armor', 'accessories', 'class_specific', 'helms', 'shields', 'chests']
        
        # 1. Uniques
        unique_data = {g: {} for g in groups + ['other']}
        for row in self.repo.get_excel_table('uniqueitems'):
            if row.get('disabled') == '1': continue
            item = self.analyzer.analyze_unique(row)
            group = self.analyzer.get_granular_group(item['item_type'])
            if item['item_type'] not in unique_data[group]: unique_data[group][item['item_type']] = []
            unique_data[group][item['item_type']].append(item)

        for group in unique_data:
            for cat, items in unique_data[group].items():
                filename = cat.lower().replace(" ", "_").replace("/", "_")
                path = os.path.join(output_dir, "uniques", group, f"{filename}.{'md' if export_format == 'markdown' else 'json'}")
                if export_format == "markdown": self.exporter.export_item_db(items, f"Unique {cat}", path) 
                else: self.json_exporter.export(items, path)

        # 2. Runewords
        rw_data = {g: {} for g in groups + ['other']}
        for row in self.repo.get_excel_table('runes'):
            if row.get('complete') != '1': continue
            rw = self.analyzer.analyze_runeword(row)
            base_cat = rw['base_items'][0] if rw['base_items'] else "Other"
            group = self.analyzer.get_granular_group(base_cat)
            if base_cat not in rw_data[group]: rw_data[group][base_cat] = []
            rw_data[group][base_cat].append(rw)

        for group in rw_data:
            for cat, rws in rw_data[group].items():
                filename = cat.lower().replace(" ", "_").replace("/", "_")
                path = os.path.join(output_dir, "runewords", group, f"{filename}.{'md' if export_format == 'markdown' else 'json'}")
                if export_format == "markdown": self.exporter.export_runewords(rws, f"{cat} Runewords", path)
                else: self.json_exporter.export(rws, path)

        # 3. Sets
        set_data = {g: {} for g in groups + ['other']}
        for row in self.repo.get_excel_table('setitems'):
            item = self.analyzer.analyze_set_item(row)
            group = self.analyzer.get_granular_group(item['item_type'])
            if item['item_type'] not in set_data[group]: set_data[group][item['item_type']] = []
            set_data[group][item['item_type']].append(item)

        for group in set_data:
            for cat, items in set_data[group].items():
                filename = cat.lower().replace(" ", "_").replace("/", "_")
                path = os.path.join(output_dir, "sets", group, f"{filename}.{'md' if export_format == 'markdown' else 'json'}")
                if export_format == "markdown": self.exporter.export_item_db(items, f"Set {cat}", path)
                else: self.json_exporter.export(items, path)

        print(f"Export to {output_dir} complete.")

def main() -> None:
    parser = argparse.ArgumentParser(description="Diablo II Item Analyzer (Refactored)")
    parser.add_argument("--mpq", default="../mods/BKDiablo/bkdiablo.mpq", help="Path to the MPQ data directory")
    parser.add_argument("--type", choices=["runeword", "unique", "export"], required=True, help="Item type to analyze or 'export' all")
    parser.add_argument("--name", help="Name of the item to search for")
    parser.add_argument("--out", default="../exports/item_db", help="Output directory for export")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown", help="Output format")
    
    args = parser.parse_args()
    repo = D2Repository(args.mpq)
    resolver = PropertyResolverService(repo, repo.load_tsv("../data/propertygroups.txt"))
    analyzer = ItemAnalyzerService(repo, resolver)
    
    if args.type == "export":
        orchestrator = ExportOrchestrator(repo, analyzer, MarkdownExporter(), JsonExporter())
        orchestrator.run_export(args.out, args.format)
    elif args.type == "unique" and args.name:
        for row in repo.get_excel_table('uniqueitems'):
            if args.name.lower() in row.get('index', '').lower():
                analyzed = analyzer.analyze_unique(row)
                if args.format == "markdown":
                    print(f"### {analyzed['display_name']} ({analyzed['id']})\n" + "\n".join([f"  * {p['resolved_text']}" for p in analyzed['properties']]))
                else: print(json.dumps(analyzed, indent=2))
                return

if __name__ == "__main__":
    main()
