with open("mods/BKDiablo/bkdiablo.mpq/data/global/excel/skills.txt", 'r', encoding='utf-8', errors='ignore') as f:
    for i in range(160):
        line = f.readline()
        if "War Cry" in line:
            print(f"Line {i}: {line[:100]}...")
