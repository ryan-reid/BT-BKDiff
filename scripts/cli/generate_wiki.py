import argparse
import os

from d2lib.wiki import WikiGenerator


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a static HTML/CSS/JS wiki site from current project exports.")
    parser.add_argument("--item-db", default="../exports/item_db", help="Path to the structured BK item database export")
    parser.add_argument("--old-item-db", default="../exports/item_db_retail", help="Optional path to the structured comparison item database export")
    parser.add_argument("--skill-trees", default="../output/skill_trees", help="Path to generated class skill tree markdown")
    parser.add_argument("--out", default="../output/wiki", help="Output directory for generated wiki pages")
    parser.add_argument("--old-label", default="Retail", help="Display label for the comparison source")
    parser.add_argument("--new-label", default="BKDiablo", help="Display label for the current export")
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    scripts_root = os.path.dirname(script_dir)
    item_db_dir = os.path.normpath(os.path.join(scripts_root, args.item_db))
    old_item_db_dir = os.path.normpath(os.path.join(scripts_root, args.old_item_db)) if args.old_item_db else None
    skill_tree_dir = os.path.normpath(os.path.join(scripts_root, args.skill_trees))
    output_dir = os.path.normpath(os.path.join(scripts_root, args.out))

    generator = WikiGenerator(
        item_db_dir,
        skill_tree_dir,
        output_dir,
        old_item_db_dir=old_item_db_dir,
        old_label=args.old_label,
        new_label=args.new_label,
    )
    generator.generate()
    print(f"Generated wiki pages in {output_dir}")


if __name__ == "__main__":
    main()
