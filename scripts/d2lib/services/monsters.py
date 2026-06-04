from __future__ import annotations
from typing import List, Dict, Optional, Any
from d2lib.repository import D2Repository, D2RepositoryProtocol, normalize_d2_value
from d2lib.models import MonsterDTO, MonsterActGroupDTO
from d2lib.services.base import _status_for_row

class MonsterAnalyzerService:
    def __init__(self, repo: D2RepositoryProtocol, retail_repo: Optional[D2RepositoryProtocol] = None):
        self.repo = repo
        self.retail_repo = retail_repo
        self.monstats = repo.get_excel_table('monstats')
        self.levels = repo.get_excel_table('levels')
        self.monstats2 = {row['Id']: row for row in repo.get_excel_table('monstats2') if row.get('Id')}
        self.retail_monstats = {
            row.get('Id', '').strip(): row
            for row in retail_repo.get_excel_table('monstats')
        } if retail_repo else {}

    def analyze_monsters(self) -> List[MonsterActGroupDTO]:
        monsters: List[MonsterDTO] = []

        # Map spawn areas
        area_map: Dict[str, List[str]] = {}
        for l_row in self.levels:
            area_name = self.repo.get_string(l_row.get('LevelName', '')) or l_row.get('LevelName', 'Unknown')
            prefixes = ["mon", "nmon", "umon"]
            for p in prefixes:
                for i in range(1, 26):
                    m_id = l_row.get(f"{p}{i}", "").strip()
                    if m_id and m_id != "0":
                        if m_id not in area_map: area_map[m_id] = []
                        if area_name not in area_map[m_id]: area_map[m_id].append(area_name)

        for row in self.monstats:
            m_id = row.get('Id', '').strip()
            if not m_id: continue

            # Filter: only include monsters that are actually used/spawnable or bosses
            spawn_areas = area_map.get(m_id, [])
            is_boss = row.get('isBoss', '0') == '1'
            if not spawn_areas and not is_boss: continue

            name_str = row.get('NameStr', '')
            name = self.repo.get_string(name_str) or name_str or m_id

            # Simple HP/Level read
            def to_int(v):
                try: return int(v) if v else 0
                except: return 0

            resists_hell = {
                "Physical": to_int(row.get('ResDm(H)')),
                "Magic": to_int(row.get('ResMa(H)')),
                "Fire": to_int(row.get('ResFi(H)')),
                "Lightning": to_int(row.get('ResLi(H)')),
                "Cold": to_int(row.get('ResCo(H)')),
                "Poison": to_int(row.get('ResPo(H)'))
            }
            immunities = [k for k, v in resists_hell.items() if v >= 100]

            monsters.append({
                "id": m_id,
                "name": name,
                "level_norm": to_int(row.get('Level')),
                "level_nm": to_int(row.get('Level(N)')),
                "level_hell": to_int(row.get('Level(H)')),
                "hp_norm": f"{row.get('MinHP')}-{row.get('MaxHP')}",
                "hp_nm": f"{row.get('MinHP(N)')}-{row.get('MaxHP(N)')}",
                "hp_hell": f"{row.get('MinHP(H)')}-{row.get('MaxHP(H)')}",
                "resists_hell": resists_hell,
                "immunities_hell": immunities,
                "spawn_areas": sorted(spawn_areas),
                "is_boss": is_boss,
                "is_unique": False, # Simplified
                "status": _status_for_row(m_id, row, self.retail_monstats) if self.retail_repo else "unchanged",
                "changed_fields": self._changed_fields(row, self.retail_monstats.get(m_id)) if self.retail_repo else [],
            })

        return [{"act": "All Monsters", "monsters": sorted(monsters, key=lambda x: x["name"])}]

    def _changed_fields(self, row: Dict[str, str], old_row: Optional[Dict[str, str]]) -> List[str]:
        if not old_row:
            return []
        interesting = [
            "Level(H)", "MinHP(H)", "MaxHP(H)", "ResDm(H)", "ResMa(H)", "ResFi(H)",
            "ResLi(H)", "ResCo(H)", "ResPo(H)", "Velocity", "Run", "A1MinD(H)",
            "A1MaxD(H)", "A2MinD(H)", "A2MaxD(H)"
        ]
        return [
            field for field in interesting
            if normalize_d2_value(row.get(field, "")) != normalize_d2_value(old_row.get(field, ""))
        ]
