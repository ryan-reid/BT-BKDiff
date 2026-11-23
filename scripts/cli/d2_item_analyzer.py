import os
import argparse
import sys
import json
from typing import List, Dict, Optional
from d2lib.repository import D2Repository
from d2lib.services import PropertyResolverService, ItemAnalyzerService
from d2lib.services.resolver import load_property_groups
from d2lib.exporters import MarkdownExporter, JsonExporter

class ExportOrchestrator:
    def __init__(self, repo: D2Repository, analyzer: ItemAnalyzerService, exporter: MarkdownExporter, json_exporter: JsonExporter):
        self.repo = repo
        self.analyzer = analyzer
        self.exporter = exporter
        self.json_exporter = json_exporter

    def run_export(self, output_dir: str, export_format: str):
        # Clear output directory to prevent stale files (e.g. from renamed categories)
        if os.path.exists(output_dir):
            import shutil
            for sub in ["uniques", "sets", "runewords"]:
                sub_path = os.path.join(output_dir, sub)
                if os.path.exists(sub_path):
                    shutil.rmtree(sub_path)

        # 1. Uniques
        unique_data = {"Weapons": {}, "Others": {}}
        for row in self.repo.get_excel_table('uniqueitems'):
            if row.get('disabled') == '1': continue
            item = self.analyzer.analyze_unique(row)
            top_group, granular_code, granular_label = self.analyzer.get_unique_export_groups(row)

            if top_group not in unique_data: top_group = "Others"

            if granular_code not in unique_data[top_group]:
                unique_data[top_group][granular_code] = (granular_label, [])
            unique_data[top_group][granular_code][1].append(item)

        for top in unique_data:
            for granular_code, (granular_label, items) in unique_data[top].items():
                safe_name = granular_code.lower().replace(" ", "_").replace("/", "_")
                path = os.path.join(output_dir, "uniques", top.lower(), f"{safe_name}.{'md' if export_format == 'markdown' else 'json'}")
                if export_format == "markdown": self.exporter.export_item_db(items, f"Unique {granular_label}", path)
                else: self.json_exporter.export(items, path)

        # 2. Runewords
        rw_groups = {"helms", "weapons", "chests", "shields"}
        rw_data = {g: {} for g in rw_groups}
        for row in self.repo.get_excel_table('runes'):
            if row.get('complete') != '1': continue
            rw = self.analyzer.analyze_runeword(row)
            group, base_code, base_label = self.analyzer.get_runeword_export_group(row)
            if group not in rw_data:
                group = "weapons"
            if base_code not in rw_data[group]:
                rw_data[group][base_code] = (base_label, [])
            rw_data[group][base_code][1].append(rw)

        for group in rw_groups:
            for base_code, (base_label, rws) in rw_data[group].items():
                filename = base_code.lower().replace(" ", "_").replace("/", "_")
                path = os.path.join(output_dir, "runewords", group, f"{filename}.{'md' if export_format == 'markdown' else 'json'}")
                if export_format == "markdown": self.exporter.export_runewords(rws, f"{base_label} Runewords", path)
                else: self.json_exporter.export(rws, path)

        # 3. Sets
        set_data = {"normal": {}, "expansion": {}}
        for row in self.repo.get_excel_table('setitems'):
            item = self.analyzer.analyze_set_item(row)
            is_expansion = item.get('is_expansion', False)
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

def run(mpq_path: str, output_dir: str, export_format: str, repo: Optional[D2Repository] = None, property_groups: Optional[List[Dict[str, str]]] = None):
    if not repo:
        repo = D2Repository(mpq_path)
    
    if property_groups is None:
        scripts_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        prop_groups_path = os.path.join(os.path.dirname(scripts_dir), "data", "propertygroups.txt")
        property_groups = load_property_groups(repo, prop_groups_path)
    
    resolver = PropertyResolverService(repo, property_groups)
    analyzer = ItemAnalyzerService(repo, resolver)
    
    orchestrator = ExportOrchestrator(repo, analyzer, MarkdownExporter(), JsonExporter())
    orchestrator.run_export(output_dir, export_format)

def main() -> None: 
    parser = argparse.ArgumentParser(description="Diablo II Item Analyzer (Refactored)")
    parser.add_argument("--mpq", default="../mods/BKDiablo/bkdiablo.mpq", help="Path to the MPQ data directory")
    parser.add_argument("--type", choices=["runeword", "unique", "export"], required=True, help="Item type to analyze or 'export' all")
    parser.add_argument("--name", help="Name of the item to search for")
    parser.add_argument("--out", default="../exports/item_db", help="Output directory for export")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown", help="Output format")
    
    args = parser.parse_args()
    
    if args.type == "export":
        run(args.mpq, args.out, args.format)
    elif args.type == "unique" and args.name:
        repo = D2Repository(args.mpq)
        scripts_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        prop_groups_path = os.path.join(os.path.dirname(scripts_dir), "data", "propertygroups.txt")
        resolver = PropertyResolverService(repo, load_property_groups(repo, prop_groups_path))
        analyzer = ItemAnalyzerService(repo, resolver)
        for row in repo.get_excel_table('uniqueitems'):
            if args.name.lower() in row.get('index', '').lower():
                analyzed = analyzer.analyze_unique(row)
                if args.format == "markdown":
                    print(f"### {analyzed['display_name']} ({analyzed['id']})\n" + "\n".join([f"  * {p['resolved_text']}" for p in analyzed['properties']]))
                else: print(json.dumps(analyzed, indent=2))
                return

if __name__ == "__main__":
    main()
