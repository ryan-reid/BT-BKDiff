import os
import sys
import argparse
from typing import Optional, Dict
from d2lib.repository import D2Repository
from d2lib.services import SkillAnalyzerService
from d2lib.exporters import MarkdownExporter

def run(mpq_path: str, out_dir: str, repo: Optional[D2Repository] = None):
    if not repo:
        repo = D2Repository(mpq_path)
    service = SkillAnalyzerService(repo)
    exporter = MarkdownExporter()

    classes = ["nec", "bar", "ama", "sor", "pal", "dru", "ass", "war"]
    
    summary = "# Skill Trees\n\n"

    for cc in classes:
        print(f"Generating skill tree for {cc.upper()}...")
        tree = service.generate_skill_tree(cc)
        out_path = os.path.join(out_dir, f"{cc}_skills.md")
        exporter.export_skill_tree(tree, out_path)
        summary += f"- [{tree['class_name']}]({cc}_skills.md)\n"
        
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "SUMMARY.md"), "w", encoding="utf-8") as f:
        f.write(summary)
    print("All skill trees generated successfully.")

def main():
    parser = argparse.ArgumentParser(description="Extract and generate skill trees")
    parser.add_argument("--mpq", default="../mods/BKDiablo/bkdiablo.mpq", help="Path to mod directory or MPQ")
    parser.add_argument("--out", default="../output/skill_trees", help="Output directory")
    args = parser.parse_args()

    run(args.mpq, args.out)

if __name__ == "__main__":
    main()

