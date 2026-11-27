import argparse
import os
import posixpath
from typing import Any, Dict, List, Optional, Tuple

from d2lib.repository import D2Repository, locale_to_html_lang
from d2lib.wiki import MediaWikiPublisher, WikiGenerator
from d2lib.wiki.i18n import locale_display_name
from d2lib.wiki.renderers import WikiPublisher, HtmlWikiRenderer
from d2lib.wiki.routes import WikiRoutes


def parse_locales(locale: str = "enUS", locales: str = "") -> List[str]:
    """Return deduplicated target locales preserving order (first is primary)."""
    raw_items = [part.strip() for part in str(locales or "").split(",") if part.strip()]
    if not raw_items:
        clean_default = str(locale or "enUS").strip() or "enUS"
        raw_items = [clean_default]
    ordered: List[str] = []
    seen = set()
    for item in raw_items:
        key = item.casefold()
        if key not in seen:
            seen.add(key)
            ordered.append(item)
    return ordered or ["enUS"]


def run(
    item_db_dir: Optional[str] = None,
    skill_tree_dir: str = "",
    output_dir: str = "",
    old_item_db_dir: Optional[str] = None,
    game_data_dir: Optional[str] = None,
    retail_data_dir: Optional[str] = None,
    layout_data_dir: Optional[str] = None,
    old_label: str = "Retail",
    new_label: str = "BKDiablo",
    mediawiki_output_dir: Optional[str] = None,
    bt_item_db_dir: Optional[str] = None,
    bt_data_dir: Optional[str] = None,
    locale: str = "enUS",
    locales: Optional[List[str]] = None,
    repo: Optional[D2Repository] = None,
    retail_repo: Optional[D2Repository] = None,
    bt_repo: Optional[D2Repository] = None,
):
    if bt_item_db_dir and not bt_data_dir:
        raise ValueError("BT data path is required when BT item database path is provided")
    bt_compare = bool(bt_data_dir)
    if bt_compare:
        for path in [p for p in (bt_item_db_dir, bt_data_dir) if p]:
            if not os.path.isdir(path):
                raise ValueError(f"Missing BT comparison input: {path}")

    target_locales = parse_locales(locale, ",".join(locales)) if locales is not None else parse_locales(locale)
    secondary_locales = target_locales[1:]
    primary_site = None
    built_jobs: List[Dict[str, Any]] = []

    for index, loc in enumerate(target_locales):
        is_primary = index == 0
        loc_output_dir = output_dir if is_primary else os.path.join(output_dir, loc)
        base_asset_prefix = "" if is_primary else "../"
        loc_repo = repo if repo is not None and getattr(repo, "locale", loc) == loc else None
        loc_retail_repo = retail_repo if retail_repo is not None and getattr(retail_repo, "locale", loc) == loc else None
        loc_bt_repo = bt_repo if bt_repo is not None and getattr(bt_repo, "locale", loc) == loc else None

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
            locale=loc,
            repo=loc_repo,
            retail_repo=loc_retail_repo,
            asset_root_prefix=base_asset_prefix,
            emit_shared_assets=is_primary,
        )
        site = generator.build_site()
        if is_primary:
            primary_site = site

        preserved: List[str] = []
        if bt_compare:
            preserved.append("compare-bt")
        if is_primary:
            preserved.extend(secondary_locales)

        bt_output: Optional[str] = None
        bt_site = None
        if bt_compare:
            bt_output = os.path.join(loc_output_dir, "compare-bt")
            bt_asset_prefix = "../" if is_primary else "../../"
            bt_site = WikiGenerator(
                # Both builders discover source reports beside the main wiki output.
                # Only the publisher changes the destination to compare-bt/.
                item_db_dir, skill_tree_dir, output_dir,
                old_item_db_dir=bt_item_db_dir, old_label="BTDiablo", new_label=new_label,
                game_data_dir=game_data_dir, retail_data_dir=bt_data_dir,
                layout_data_dir=layout_data_dir, locale=loc,
                repo=loc_repo, retail_repo=loc_bt_repo,
                asset_root_prefix=bt_asset_prefix,
                emit_shared_assets=False,
            ).build_site()
            add_comparison_links(site, bt_site)

        built_jobs.append({
            "locale": loc,
            "is_primary": is_primary,
            "loc_output_dir": loc_output_dir,
            "preserved": preserved,
            "site": site,
            "bt_output": bt_output,
            "bt_site": bt_site,
        })

    if len(built_jobs) > 1:
        add_locale_links([(job["locale"], job["is_primary"], False, job["site"]) for job in built_jobs])
        if bt_compare:
            add_locale_links([(job["locale"], job["is_primary"], True, job["bt_site"]) for job in built_jobs])

    for job in built_jobs:
        if bt_compare and job["bt_site"] is not None and job["bt_output"] is not None:
            WikiPublisher(job["loc_output_dir"]).publish(job["site"], HtmlWikiRenderer(), preserved_prefixes=job["preserved"])
            WikiPublisher(job["bt_output"]).publish(job["bt_site"], HtmlWikiRenderer())
        else:
            WikiPublisher(job["loc_output_dir"]).publish(job["site"], HtmlWikiRenderer(), preserved_prefixes=job["preserved"])

    print(f"Generated wiki pages in {output_dir} (locales: {', '.join(target_locales)})")
    if mediawiki_output_dir and primary_site is not None:
        MediaWikiPublisher(mediawiki_output_dir).publish(primary_site)
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


def add_locale_links(locale_sites: List[Tuple[str, bool, bool, Dict[str, Any]]]) -> None:
    """Attach relative language switcher links across built locale subtrees."""
    if len(locale_sites) <= 1:
        return

    def _subtree_prefix(is_primary: bool, is_bt: bool, loc: str) -> str:
        base = "" if is_primary else f"{loc}/"
        return f"{base}compare-bt/" if is_bt else base

    paths_by_locale = {
        loc: {page["output_path"] for page in site.get("pages", [])}
        for loc, _, _, site in locale_sites
    }
    for loc, is_primary, is_bt, site in locale_sites:
        cur_prefix = _subtree_prefix(is_primary, is_bt, loc)
        for page in site.get("pages", []):
            cur_path = page["output_path"]
            cur_full = f"{cur_prefix}{cur_path}"
            cur_dir = posixpath.dirname(cur_full) or "."
            options = []
            for target_loc, target_primary, target_bt, _ in locale_sites:
                target_page = cur_path if cur_path in paths_by_locale[target_loc] else "index.html"
                target_full = f"{_subtree_prefix(target_primary, target_bt, target_loc)}{target_page}"
                options.append({
                    "locale": target_loc,
                    "html_lang": locale_to_html_lang(target_loc),
                    "label": locale_display_name(target_loc),
                    "href": posixpath.relpath(target_full, cur_dir),
                    "active": target_loc == loc,
                })
            page.setdefault("payload", {})["locale_switch"] = {
                "active": loc,
                "options": options,
            }


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a static HTML/CSS/JS wiki site from game data repositories.")
    parser.add_argument("--item-db", default="", help="Optional legacy path to structured BK item database JSON exports")
    parser.add_argument("--old-item-db", default="", help="Optional legacy path to structured comparison item database JSON exports")
    parser.add_argument("--skill-trees", default="../output/skill_trees", help="Legacy compatibility argument; skills now come directly from game data")
    parser.add_argument("--game-data", default="../mods/BKDiablo/bkdiablo.mpq", help="Path to the BK game data root")
    parser.add_argument("--retail-data", default="../data/retail", help="Path to the Retail game data root")
    parser.add_argument(
        "--layout-data",
        default="",
        help="Optional path to a data root or global/tiles folder for DS1 layout files (defaults to D2R_LAYOUT_DATA_DIR or D2R_DATA_DIR env var if set)",
    )
    parser.add_argument("--out", default="../output/wiki", help="Output directory for generated wiki pages")
    parser.add_argument("--mediawiki-out", default="", help="Optional output directory for generated MediaWiki wikitext files")
    parser.add_argument("--old-label", default="Retail", help="Display label for the comparison source")
    parser.add_argument("--new-label", default="BKDiablo", help="Display label for the current export")
    parser.add_argument("--compare-bt", action="store_true", help="Build Retail and BTDiablo comparisons with a site-wide switch")
    parser.add_argument("--bt-item-db", default="", help="Optional legacy path to structured BT item database JSON exports")
    parser.add_argument("--bt-data", default="../mods/BTDiablo/btdiablo.mpq")
    parser.add_argument("--locale", default="enUS", help="Target string locale code (e.g. enUS, deDE, koKR)")
    parser.add_argument(
        "--locales",
        default="",
        help="Comma-separated locale codes to build (first is primary at root; others under <out>/<locale>/). Overrides --locale when set.",
    )
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    scripts_root = os.path.dirname(script_dir)
    item_db_dir = os.path.normpath(os.path.join(scripts_root, args.item_db)) if args.item_db else None
    old_item_db_dir = os.path.normpath(os.path.join(scripts_root, args.old_item_db)) if args.old_item_db else None
    skill_tree_dir = os.path.normpath(os.path.join(scripts_root, args.skill_trees))
    game_data_dir = os.path.normpath(os.path.join(scripts_root, args.game_data))
    retail_data_dir = os.path.normpath(os.path.join(scripts_root, args.retail_data))
    env_layout_data = os.environ.get("D2R_LAYOUT_DATA_DIR", "").strip() or os.environ.get("D2R_DATA_DIR", "").strip()
    layout_data_dir = (
        os.path.normpath(os.path.join(scripts_root, args.layout_data))
        if args.layout_data
        else (os.path.normpath(env_layout_data) if env_layout_data else None)
    )
    output_dir = os.path.normpath(os.path.join(scripts_root, args.out))
    mediawiki_output_dir = os.path.normpath(os.path.join(scripts_root, args.mediawiki_out)) if args.mediawiki_out else None
    target_locales = parse_locales(args.locale, args.locales)

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
        bt_item_db_dir=os.path.normpath(os.path.join(scripts_root, args.bt_item_db)) if (args.compare_bt and args.bt_item_db) else None,
        bt_data_dir=os.path.normpath(os.path.join(scripts_root, args.bt_data)) if args.compare_bt else None,
        locale=target_locales[0],
        locales=target_locales,
    )


if __name__ == "__main__":
    main()
