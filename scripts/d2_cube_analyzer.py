import os
import argparse
import sys
from d2_repository import D2Repository
from d2_services import CubeAnalyzerService
from d2_exporters import MarkdownExporter, JsonExporter

def main() -> None:
    parser = argparse.ArgumentParser(description="Diablo II Cube Recipe Analyzer")
    parser.add_argument("--mpq", default="../mods/BKDiablo/bkdiablo.mpq", help="Path to the MPQ data directory")
    parser.add_argument("--out", default="../output/bk_cubemain_detailed.md", help="Output file path")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown", help="Output format")
    
    args = parser.parse_args()
    retail_path = "E:\\Games\\Diablo II Resurrected\\Data"
    repo = D2Repository(args.mpq, retail_path=retail_path)
    analyzer = CubeAnalyzerService(repo)
    exporter = MarkdownExporter()
    
    recipes = repo.get_excel_table('cubemain')
    analyzed_recipes = [analyzer.analyze_recipe(row) for row in recipes]
    
    enabled_recipes = [r for r in analyzed_recipes if r['enabled']]
    disabled_recipes = [r for r in analyzed_recipes if not r['enabled']]
    
    if args.format == "markdown":
        # We need a specialized method for cube recipes in the exporter
        exporter.export_cube_recipes(enabled_recipes, "Horadric Cube Recipes (BK Diablo)", args.out)
        
        # Also export disabled recipes to a separate file
        disabled_out = args.out.replace(".md", "_disabled.md")
        exporter.export_cube_recipes(disabled_recipes, "Disabled Horadric Cube Recipes (BK Diablo)", disabled_out)
        print(f"Enabled recipes exported to {args.out}")
        print(f"Disabled recipes exported to {disabled_out}")
    else:
        # JSON export
        json_exporter = JsonExporter()
        json_exporter.export(analyzed_recipes, args.out.replace(".md", ".json"))
        print(f"All recipes exported to {args.out.replace('.md', '.json')}")

if __name__ == "__main__":
    main()
