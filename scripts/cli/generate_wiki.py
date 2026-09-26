import argparse
import os
from typing import Optional

from d2lib.wiki import MediaWikiPublisher, WikiGenerator
from d2lib.wiki.renderers import WikiPublisher, HtmlWikiRenderer
from d2lib.wiki.routes import WikiRoutes


def run(
    item_db_dir: str,
    skill_tree_dir: str,
    output_dir: str,
    old_item_db_dir: Optional[str] = None,
    game_data_dir: Optional[str] = None,
    retail_data_dir: Optional[str] = None,
    layout_data_dir: Optional[str] = None,
    old_label: str = "Retail",
    new_label: str = "BKDiablo",
    mediawiki_output_dir: Optional[str] = None,
    bt_item_db_dir: Optional[str] = None,
    bt_data_dir: Optional[str] = None,
):
    generator = WikiGenerator(
        item_db_dir,
        skill_tree_dir,
        output_dir,
        old_item_db_dir=old_item_db_dir,
        old_label=old_label,
        new_label=new_label,
        game_data_dir=game_data_dir,
        retail_data_dir=retail_data_dir,
        layout_data_dir=layout_data_dir,
    )
    if bool(bt_item_db_dir) != bool(bt_data_dir):
        raise ValueError("Both BT item database and BT data paths are required")
    if bt_item_db_dir:
        for path in (bt_item_db_dir, bt_data_dir):
            if not os.path.isdir(path):
                raise ValueError(f"Missing BT comparison input: {path}")
        site = generator.build_site()
        bt_output = os.path.join(output_dir, "compare-bt")
        bt_site = WikiGenerator(
            item_db_dir, skill_tree_dir, bt_output,
            old_item_db_dir=bt_item_db_dir, old_label="BTDiablo", new_label=new_label,
            game_data_dir=game_data_dir, retail_data_dir=bt_data_dir,
            layout_data_dir=layout_data_dir,
        ).build_site()
        add_comparison_links(site, bt_site)
        WikiPublisher(output_dir).publish(site, HtmlWikiRenderer())
        WikiPublisher(bt_output).publish(bt_site, HtmlWikiRenderer())
    else:
        site = generator.generate()
    print(f"Generated wiki pages in {output_dir}")
    if mediawiki_output_dir:
        MediaWikiPublisher(mediawiki_output_dir).publish(site)
        print(f"Generated MediaWiki pages in {mediawiki_output_dir}")

def add_comparison_links(retail_site, bt_site):
    """Link counterpart pages relative to each baseline's own site root."""
    for site, other, is_bt in ((retail_site, bt_site, False), (bt_site, retail_site, True)):
        other_paths = {page["output_path"] for page in other["pages"]}
        for page in site["pages"]:
            path = page["output_path"]
            root = WikiRoutes.site_root_for_output_path(path)
            target = path if path in other_paths else "index.html"
            page["payload"]["comparison_switch"] = {
                "active": "bt" if is_bt else "retail",
                "retail": root + ("../" + target if is_bt else path),
                "bt": root + (path if is_bt else "compare-bt/" + target),
            }


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a static HTML/CSS/JS wiki site from current project exports.")
    parser.add_argument("--item-db", default="../exports/item_db", help="Path to the structured BK item database export")
    parser.add_argument("--old-item-db", default="../exports/item_db_retail", help="Optional path to the structured comparison item database export")
    parser.add_argument("--skill-trees", default="../output/skill_trees", help="Path to generated class skill tree markdown")
    parser.add_argument("--game-data", default="../mods/BKDiablo/bkdiablo.mpq", help="Path to the BK game data root")
    parser.add_argument("--retail-data", default="../data/retail", help="Path to the Retail game data root")
    parser.add_argument("--layout-data", default="", help="Optional path to a data root or global/tiles folder for DS1 layout files")
    parser.add_argument("--out", default="../output/wiki", help="Output directory for generated wiki pages")
    parser.add_argument("--mediawiki-out", default="", help="Optional output directory for generated MediaWiki wikitext files")
    parser.add_argument("--old-label", default="Retail", help="Display label for the comparison source")
    parser.add_argument("--new-label", default="BKDiablo", help="Display label for the current export")
    parser.add_argument("--compare-bt", action="store_true", help="Build Retail and BTDiablo comparisons with a site-wide switch")
    parser.add_argument("--bt-item-db", default="../exports/item_db_bt")
    parser.add_argument("--bt-data", default="../mods/BTDiablo/btdiablo.mpq")
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    scripts_root = os.path.dirname(script_dir)
    item_db_dir = os.path.normpath(os.path.join(scripts_root, args.item_db))
    old_item_db_dir = os.path.normpath(os.path.join(scripts_root, args.old_item_db)) if args.old_item_db else None
    skill_tree_dir = os.path.normpath(os.path.join(scripts_root, args.skill_trees))
    game_data_dir = os.path.normpath(os.path.join(scripts_root, args.game_data))
    retail_data_dir = os.path.normpath(os.path.join(scripts_root, args.retail_data))
    layout_data_dir = os.path.normpath(os.path.join(scripts_root, args.layout_data)) if args.layout_data else None
    output_dir = os.path.normpath(os.path.join(scripts_root, args.out))
    mediawiki_output_dir = os.path.normpath(os.path.join(scripts_root, args.mediawiki_out)) if args.mediawiki_out else None

    run(
        item_db_dir,
        skill_tree_dir,
        output_dir,
        old_item_db_dir=old_item_db_dir,
        game_data_dir=game_data_dir,
        retail_data_dir=retail_data_dir,
        layout_data_dir=layout_data_dir,
        old_label=args.old_label,
        new_label=args.new_label,
        mediawiki_output_dir=mediawiki_output_dir,
        bt_item_db_dir=os.path.normpath(os.path.join(scripts_root, args.bt_item_db)) if args.compare_bt else None,
        bt_data_dir=os.path.normpath(os.path.join(scripts_root, args.bt_data)) if args.compare_bt else None,
    )


if __name__ == "__main__":
    main()
