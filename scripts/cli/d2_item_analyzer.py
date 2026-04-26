import os
import argparse
import sys
import json
from typing import List, Dict, Optional
from d2lib.repository import D2Repository
from d2lib.services import PropertyResolverService, ItemAnalyzerService
from d2lib.exporters import MarkdownExporter, JsonExporter

class ExportOrchestrator:
    def __init__(self, repo: D2Repository, analyzer: ItemAnalyzerService, exporter: MarkdownExporter, json_exporter: JsonExporter):
        self.repo = repo
        self.analyzer = analyzer
        self.exporter = exporter
        self.json_exporter = json_exporter

    def run_export(self, output_dir: str, export_format: str):
        # 1. Uniques
        unique_data = {"Weapons": {}, "Others": {}}
        for row in self.repo.get_excel_table('uniqueitems'):
            if row.get('disabled') == '1': continue
            item = self.analyzer.analyze_unique(row)
            granular_group = self.analyzer.get_granular_group(item['item_type'])
            top_group = self.analyzer.get_top_level_group(granular_group)
            
            if top_group not in unique_data: top_group = "Others"
            
            if granular_group not in unique_data[top_group]:
                unique_data[top_group][granular_group] = []
            unique_data[top_group][granular_group].append(item)

        for top in unique_data:
            for granular, items in unique_data[top].items():
                safe_name = granular.lower().replace(" ", "_").replace("/", "_")
                path = os.path.join(output_dir, "uniques", top.lower(), f"{safe_name}.{'md' if export_format == 'markdown' else 'json'}")
                if export_format == "markdown": self.exporter.export_item_db(items, f"Unique {granular}", path) 
                else: self.json_exporter.export(items, path)

        # 2. Runewords
        rw_groups = {"helms": "Helms", "weapons": "Weapons", "chests": "Chests", "shields": "Shields"}
        rw_data = {g: {} for g in rw_groups}
        for row in self.repo.get_excel_table('runes'):
            if row.get('complete') != '1': continue
            rw = self.analyzer.analyze_runeword(row)
            base_cat = rw['base_items'][0] if rw['base_items'] else "Other"
            
            # Map to one of the 4 major categories
            cat_lower = base_cat.lower()
            if any(h in cat_lower for h in ['helm', 'circlet', 'pelt', 'primal', 'merc']): group = "helms"
            elif any(s in cat_lower for s in ['shield', 'auric', 'voodoo']): group = "shields"
            elif any(c in cat_lower for c in ['armor', 'tors']): group = "chests"
            else: group = "weapons"
            
            if base_cat not in rw_data[group]: rw_data[group][base_cat] = []
            rw_data[group][base_cat].append(rw)

        for group, label in rw_groups.items():
            for cat, rws in rw_data[group].items():
                filename = cat.lower().replace(" ", "_").replace("/", "_")
                path = os.path.join(output_dir, "runewords", group, f"{filename}.{'md' if export_format == 'markdown' else 'json'}")
                if export_format == "markdown": self.exporter.export_runewords(rws, f"{cat} Runewords", path)
                else: self.json_exporter.export(rws, path)

        # 3. Sets
        set_data = {"normal": {}, "expansion": {}}
        for row in self.repo.get_excel_table('setitems'):
            item = self.analyzer.analyze_set_item(row)
            is_expansion = item['raw_row'].get('is_expansion', False)
            group = "expansion" if is_expansion else "normal"
            
            if item['item_type'] not in set_data[group]:
                set_data[group][item['item_type']] = []
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
