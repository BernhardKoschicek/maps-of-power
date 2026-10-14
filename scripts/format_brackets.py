import glob
from pathlib import Path
import re
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent

if len(sys.argv) > 1:
    target_files = [Path(p) for p in sys.argv[1:]]
else:
    data_pattern = str(ROOT_DIR / 'mop/data/*.py')
    target_files = [Path(p) for p in glob.glob(data_pattern)]

for file_path in target_files:
    if not file_path.exists():
        continue
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Drop trailing comma before a closing bracket on a new line
    while re.search(r',\n[ \t]*([\]})]+)', content):
        content = re.sub(r',\n[ \t]*([\]})]+)', r'\1', content)
        
    # Move closing brackets to the previous line
    while re.search(r'\n[ \t]*([\]})]+)', content):
        content = re.sub(r'\n[ \t]*([\]})]+)', r'\1', content)
        
    # Fix missing spaces from array of dicts: '},{' -> '}, {'
    content = content.replace('},{', '}, {')

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
