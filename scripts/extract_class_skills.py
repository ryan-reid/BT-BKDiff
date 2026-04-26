import os
import sys
import argparse
from d2_repository import D2Repository
from d2_services import SkillAnalyzerService
from d2_exporters import MarkdownExporter

def main():
    parser = argparse.ArgumentParser(description="Extract and generate skill trees")
    parser.add_argument("--mpq", default="../mods/BKDiablo/bkdiablo.mpq", help="Path to mod directory or MPQ")
    parser.add_argument("--out", default="../output/skill_trees", help="Output directory")
    args = parser.parse_args()

    repo = D2Repository(args.mpq)
    service = SkillAnalyzerService(repo)
    exporter = MarkdownExporter()

    classes = ["nec", "bar", "ama", "sor", "pal", "dru", "asn", "war"]
    
    summary = "# Skill Trees\n\n"

    for cc in classes:
        print(f"Generating skill tree for {cc.upper()}...")
        tree = service.generate_skill_tree(cc)
        out_path = os.path.join(args.out, f"{cc}_skills.md")
        exporter.export_skill_tree(tree, out_path)
        summary += f"- [{tree['class_name']}]({cc}_skills.md)\n"
        
    with open(os.path.join(args.out, "SUMMARY.md"), "w", encoding="utf-8") as f:
        f.write(summary)
    print("All skill trees generated successfully.")

if __name__ == "__main__":
    main()

