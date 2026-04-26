import json
import os

def load_strings():
    strings = {}
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(script_dir)
    mod_path = os.path.join(root, "mods/BKDiablo/bkdiablo.mpq")
    paths = [
        os.path.join(root, "data/base/strings"),
        os.path.join(root, "data/retail/strings"),
        os.path.join(mod_path, "data/local/lng/strings")
    ]
    for p in paths:
        if os.path.exists(p):
            for f in os.listdir(p):
                if f.endswith(".json"):
                    with open(os.path.join(p, f), 'r', encoding='utf-8-sig') as file:
                        try:
                            for entry in json.load(file):
                                k, v = entry.get('Key'), entry.get('enUS')
                                if k and v: strings[k.lower()] = v
                        except: continue
    return strings

def main():
    strings = load_strings()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(script_dir)
    skilldesc_path = os.path.join(root, "mods/BKDiablo/bkdiablo.mpq/data/global/excel/skilldesc.txt")
    
    mapping = {}
    with open(skilldesc_path, 'r') as f:
        lines = f.readlines()
        header = lines[0].split('\t')
        for line in lines[1:]:
            parts = line.split('\t')
            for i in range(len(header)):
                if header[i].startswith('descline') and i < len(parts):
                    line_id = parts[i]
                    if line_id and line_id != '0':
                        text_id = parts[i+1]
                        text = strings.get(text_id.lower(), text_id)
                        mapping[line_id] = text
    
    for k, v in sorted(mapping.items(), key=lambda x: int(x[0])):
        print(f"{k}: {v}")

if __name__ == "__main__":
    main()
