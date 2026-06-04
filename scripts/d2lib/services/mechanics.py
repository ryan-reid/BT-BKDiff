from __future__ import annotations
from typing import List, Dict, Optional, Any
from d2lib.repository import D2Repository, D2RepositoryProtocol
from d2lib.models import MechanicsSummaryDTO
from d2lib.services.comparison import ExcelComparisonService
from d2lib.services.base import _summarize_excel_diff

class MechanicsAnalyzerService:
    def __init__(self, repo: D2RepositoryProtocol, retail_repo: Optional[D2RepositoryProtocol] = None):
        self.repo = repo
        self.retail_repo = retail_repo

    def analyze_mechanics(self) -> MechanicsSummaryDTO:
        exp_changes = []
        diff_changes = []

        if self.retail_repo:
            # Compare Experience
            exp_bk = self.repo.get_excel_table('experience')
            exp_rt = self.retail_repo.get_excel_table('experience')

            exp_diff = ExcelComparisonService.compare_tables(exp_bk, exp_rt, 'Level', 'experience.txt')
            for lvl, row in exp_diff['modified_rows'].items():
                for col, vals in row.items():
                    exp_changes.append({"level": lvl, "property": col, "retail": vals['bt_old'], "bk": vals['bk_new']})

            # Compare Difficulty Levels
            dl_bk = self.repo.get_excel_table('difficultylevels')
            dl_rt = self.retail_repo.get_excel_table('difficultylevels')

            dl_diff = ExcelComparisonService.compare_tables(dl_bk, dl_rt, 'Name', 'difficultylevels.txt')
            for name, row in dl_diff['modified_rows'].items():
                for col, vals in row.items():
                    diff_changes.append({"difficulty": name, "property": col, "retail": vals['bt_old'], "bk": vals['bk_new']})

        return {
            "experience_changes": exp_changes,
            "difficulty_changes": diff_changes,
            "skill_changes": self._table_summary("skills", "skill"),
            "missile_changes": self._table_summary("missiles", "Missile"),
            "charstat_changes": self._table_summary("charstats", "class"),
            "property_changes": self._table_summary("properties", "code"),
            "itemstat_changes": self._table_summary("itemstatcost", "Stat"),
            "gamble_changes": self._table_summary("gamble", "name"),
        }

    def _table_summary(self, table_name: str, key_col: str) -> List[Dict[str, Any]]:
        if not self.retail_repo:
            return []
        bk_rows = self.repo.get_excel_table(table_name)
        retail_rows = self.retail_repo.get_excel_table(table_name)
        if not bk_rows or not retail_rows:
            return []
        diff = ExcelComparisonService.compare_tables(bk_rows, retail_rows, key_col, f"{table_name}.txt")
        return _summarize_excel_diff(diff)
