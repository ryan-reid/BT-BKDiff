import os
import sys
from d2_repository import D2Repository
from d2_services import ExcelComparisonService
from d2_exporters import MarkdownExporter

def get_key_column(filename: str) -> str:
    mapping = {
        'armor.txt': 'name', 'automagic.txt': 'Name', 'charstats.txt': 'class', 'cubemain.txt': 'description',
        'difficultylevels.txt': 'Name', 'experience.txt': 'Level', 'gamble.txt': 'name', 'gems.txt': 'name',
        'itemstatcost.txt': 'Stat', 'itemtypes.txt': 'ItemType', 'levels.txt': 'Name', 'missiles.txt': 'Missile',
        'monstats.txt': 'Id', 'properties.txt': 'code', 'skills.txt': 'skill', 'uniqueitems.txt': 'index'
    }
    return mapping.get(filename, 'code')

def main() -> None:
    bk_dir = "../mods/BKDiablo/bkdiablo.mpq/data/global/excel"
    bt_dir = "../mods/BTDiablo/btdiablo.mpq/data/global/excel"
    report_dir = "../output/excel_diff_report"
    
    repo = D2Repository(".")
    exporter = MarkdownExporter()
    
    files_bk = {f for f in os.listdir(bk_dir) if f.endswith('.txt')}
    files_bt = {f for f in os.listdir(bt_dir) if f.endswith('.txt')}
    common_files = sorted(files_bk & files_bt)
    
    for filename in common_files:
        print(f"Comparing {filename}...")
        table_bk = repo.load_tsv(os.path.join(bk_dir, filename))
        table_bt = repo.load_tsv(os.path.join(bt_dir, filename))
        
        diff = ExcelComparisonService.compare_tables(table_bk, table_bt, get_key_column(filename), filename)
        exporter.export_excel_diff(diff, os.path.join(report_dir, filename.replace('.txt', '.md')))

    print(f"Reports generated in {report_dir}")

if __name__ == "__main__":
    main()
