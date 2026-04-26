import csv

with open("mods/BKDiablo/bkdiablo.mpq/data/global/excel/skills.txt", 'r', encoding='utf-8', errors='ignore') as f:
    header = f.readline().split('\t')
    for i, h in enumerate(header):
        if 'Param' in h:
            print(f"{i}: {h.strip()}")
