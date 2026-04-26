import csv
import sys

csv.field_size_limit(1000000)

with open("mods/BKDiablo/bkdiablo.mpq/data/global/excel/skills.txt", 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()
    header = lines[0].split('\t')
    for line in lines[1:]:
        row = line.split('\t')
        if "War Cry" in row[0]:
            print(f"Match found: {row[0]}")
            for h, v in zip(header, row):
                if v and v.strip() != '0' and v.strip() != '':
                    print(f"{h.strip()}: {v.strip()}")
            break
