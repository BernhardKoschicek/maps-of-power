import glob
import re
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

for filepath in glob.glob(str(ROOT_DIR / 'mop/data/*.py')):
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Drop trailing comma before a closing bracket on a new line
    while re.search(r',\n[ \t]*([\]})]+)', content):
        content = re.sub(r',\n[ \t]*([\]})]+)', r'\1', content)
        
    # Move closing brackets to the previous line
    while re.search(r'\n[ \t]*([\]})]+)', content):
        content = re.sub(r'\n[ \t]*([\]})]+)', r'\1', content)
        
    # Fix missing spaces from array of dicts: '},{' -> '}, {'
    content = content.replace('},{', '}, {')

    with open(filepath, 'w') as f:
        f.write(content)
