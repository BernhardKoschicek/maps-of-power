"""Build SQLite database from TIB register datasets.

Parses 14 volume datasets, normalizes Greek and diacritic characters,
formats citations as '52 (A. 75)', and builds SQLite tables and FTS5 index.
"""

import glob
import json
import os
from pathlib import Path
import re
import sqlite3
from typing import Any
import unicodedata

# Map Greek characters and homoglyphs to Latin equivalents
GREEK_TO_LATIN = {
    'Α': 'A', 'α': 'a', 'Ά': 'A', 'ά': 'a',
    'Β': 'B', 'β': 'b',
    'Γ': 'G', 'γ': 'g',
    'Δ': 'D', 'δ': 'd',
    'Ε': 'E', 'ε': 'e', 'Έ': 'E', 'é': 'e',
    'Ζ': 'Z', 'ζ': 'z',
    'Η': 'E', 'η': 'e', 'Ή': 'E', 'ή': 'e',
    'Θ': 'Th', 'θ': 'th',
    'Ι': 'I', 'ι': 'i', 'Ί': 'I', 'ί': 'i', 'ϊ': 'i', 'ΐ': 'i',
    'Κ': 'K', 'κ': 'k',
    'Λ': 'L', 'λ': 'l',
    'Μ': 'M', 'μ': 'm',
    'Ν': 'N', 'ν': 'n',
    'Ξ': 'X', 'ξ': 'x',
    'Ο': 'O', 'ο': 'o', 'Ό': 'O', 'ό': 'o',
    'Π': 'P', 'π': 'p',
    'Ρ': 'R', 'ρ': 'r',
    'Σ': 'S', 'σ': 's', 'ς': 's',
    'Τ': 'T', 'τ': 't',
    'Υ': 'Y', 'υ': 'y', 'Ύ': 'Y', 'ύ': 'y', 'ϋ': 'y', 'ΰ': 'y',
    'Φ': 'Ph', 'φ': 'ph',
    'Χ': 'Ch', 'χ': 'ch',
    'Ψ': 'Ps', 'ψ': 'ps',
    'Ω': 'O', 'ω': 'o', 'Ώ': 'O', 'ώ': 'o'}


def normalize_for_search(text: str) -> str:
    """Normalize text for diacritic-insensitive and Greek-tolerant search."""
    if not text:
        return ''
    # 1. Map Greek homoglyphs and transliterations
    chars = [GREEK_TO_LATIN.get(c, c) for c in text]
    s = ''.join(chars)
    # 2. Decompose unicode accents and remove combining diacritics
    decomposed = unicodedata.normalize('NFKD', s)
    stripped = ''.join(c for c in decomposed if not unicodedata.combining(c))
    # 3. Replace common ligatures and punctuation
    cleaned = stripped.replace('ß', 'ss').replace('’', "'").replace('`', "'")
    return cleaned.lower().strip()


# pylint: disable=too-many-locals,too-many-branches,too-many-statements
def parse_page_citations(raw_pages: str) -> list[dict[str, Any]]:
    """Parse raw pages string into clean, structured citation objects."""
    if not raw_pages or not raw_pages.strip():
        return []

    s = raw_pages.replace('\xa0', ' ').replace('&nbsp;', ' ').strip()
    raw_tokens = [t.strip() for t in re.split(r',\s*', s) if t.strip()]

    # Group comma-split commentary (e.g. '52' followed by 'A. 75')
    grouped: list[dict[str, Any]] = []
    for token in raw_tokens:
        clean = re.sub(r'<[^>]+>', '', token).strip()
        is_commentary = bool(re.match(
            r'^(?:u\.\s*)?(?:A\.|Anm\.?)\s*\d+$', clean, re.IGNORECASE))
        if is_commentary and grouped:
            grouped[-1]['tokens'].append(token)
        else:
            grouped.append({'tokens': [token]})

    citations = []
    for idx, g in enumerate(grouped, start=1):
        full_str = ', '.join(g['tokens'])
        is_bold = '<b>' in full_str or '<strong>' in full_str

        # Extract link target page if present in legacy <a> tags
        target_match = re.search(r'#page/([^\"\'\s>]+)', full_str)
        target_str = target_match.group(1) if target_match else None

        # Clean HTML tags to get pure text
        text = re.sub(r'<[^>]+>', '', full_str).strip()

        # Extract commentary (e.g. 'A. 75', 'u. A. 131', 'A. 10 u. 15')
        commentary: str | None = None
        comm_m = re.search(
            r'(?:,\s*|\s+)?((?:u\.\s*)?(?:A\.|Anm\.?)\s*\d+.*)$',
            text, re.IGNORECASE)
        if comm_m and any(k in comm_m.group(1) for k in ['A.', 'Anm']):
            commentary = comm_m.group(1).strip(' ,')
            text = text[:comm_m.start()].strip(' ,')

        # Clean suffix (f., ff.)
        suffix = ''
        if text.endswith('ff.') or text.endswith('ff'):
            suffix = 'ff.'
            page = re.sub(r'ff\.?$', '', text).strip(' .u')
        elif text.endswith('f.') or text.endswith('f'):
            suffix = 'f.'
            page = re.sub(r'f\.?$', '', text).strip(' .u')
        else:
            page = text.strip(' .u')

        # Normalize dash characters (en-dash, em-dash to standard en-dash)
        page = re.sub(r'\s*[–—-]\s*', '–', page)

        # Determine start and end page numbers
        range_m = re.match(r'^(\d+)[–-](\d+)$', page)
        if range_m:
            page_start: int | None = int(range_m.group(1))
            page_end: int | None = int(range_m.group(2))
        elif page.isdigit():
            page_start = int(page)
            page_end = None
        else:
            # Fallback if non-digit characters present
            lead_m = re.match(r'^(\d+)', page)
            page_start = int(lead_m.group(1)) if lead_m else None
            page_end = None

        target_page = (
            int(target_str) if (target_str and target_str.isdigit())
            else page_start)

        # Build clean display string: '52 (A. 75)' or '181f.' or '119–121'
        disp_page = f'{page}{suffix}'
        if commentary:
            # Standardize commentary format inside parentheses
            comm_clean = re.sub(r'^(u\.\s*)', '', commentary).strip()
            display_str = f'{disp_page} ({comm_clean})'
        else:
            display_str = disp_page

        citations.append({
            'page_str': page,
            'suffix': suffix,
            'page_start': page_start,
            'page_end': page_end,
            'commentary': commentary,
            'is_main': is_bold,
            'target_page': target_page,
            'display_str': display_str,
            'seq': idx})

    return citations


# pylint: disable=too-many-locals,too-many-statements
def build_database(
        source_dir: str,
        target_db_path: str) -> None:
    """Read register files, process records, and write SQLite database."""
    print(f'Building TIB database at {target_db_path}...')
    target_path = Path(target_db_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    if target_path.exists():
        target_path.unlink()

    conn = sqlite3.connect(str(target_path))
    cur = conn.cursor()

    # Enable WAL mode for high performance concurrent reading
    cur.execute('PRAGMA journal_mode = WAL;')
    cur.execute('PRAGMA synchronous = NORMAL;')

    # Create tables
    cur.execute('''
        CREATE TABLE toponyms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            name_normalized TEXT NOT NULL,
            notes TEXT DEFAULT '',
            notes_normalized TEXT DEFAULT '',
            volume TEXT NOT NULL,
            volume_id INTEGER NOT NULL,
            pages_json TEXT NOT NULL,
            pages_display TEXT NOT NULL
        );
    ''')

    cur.execute('''
        CREATE TABLE toponym_pages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            toponym_id INTEGER NOT NULL REFERENCES toponyms(id)
                ON DELETE CASCADE,
            volume_id INTEGER NOT NULL,
            page_start INTEGER,
            page_end INTEGER,
            page_str TEXT NOT NULL,
            suffix TEXT DEFAULT '',
            commentary TEXT,
            is_main INTEGER NOT NULL DEFAULT 0,
            target_page INTEGER,
            display_str TEXT NOT NULL,
            seq INTEGER NOT NULL
        );
    ''')

    cur.execute('CREATE INDEX idx_toponyms_vol ON toponyms(volume_id);')
    cur.execute('CREATE INDEX idx_toponyms_norm ON toponyms(name_normalized);')
    cur.execute(
        'CREATE INDEX idx_pages_lookup ON toponym_pages('
        'volume_id, page_start);')
    cur.execute(
        'CREATE INDEX idx_pages_toponym ON toponym_pages(toponym_id);')

    # Full-Text Search (FTS5) table with unicode61 remove_diacritics
    cur.execute('''
        CREATE VIRTUAL TABLE toponyms_fts USING fts5(
            name,
            name_normalized,
            notes,
            notes_normalized,
            pages_display,
            volume,
            content='toponyms',
            content_rowid='id',
            tokenize='unicode61 remove_diacritics 2'
        );
    ''')

    # Load and process volume files
    files = sorted(glob.glob(os.path.join(source_dir, 'tib*.py')))
    total_toponyms = 0
    total_pages = 0

    for filepath in files:
        ns: dict[str, Any] = {}
        with open(filepath, 'r', encoding='utf-8') as fp:
            exec(fp.read(), ns)  # pylint: disable=exec-used

        vol_rows: list[dict[str, Any]] = []
        for v in ns.values():
            if isinstance(v, list):
                vol_rows = v
                break

        if not vol_rows:
            continue

        vol_name = vol_rows[0].get('Volume', 'TIB')
        vol_id_m = re.search(r'\d+', vol_name)
        vol_id = int(vol_id_m.group(0)) if vol_id_m else 0

        print(f'Processing {Path(filepath).name}: {len(vol_rows)} rows '
              f'({vol_name})...')

        for r in vol_rows:
            name = r.get('Name', '').strip()
            notes = r.get('Notes', '').strip()
            raw_pages = r.get('Pages', '')

            citations = parse_page_citations(raw_pages)
            disp_citations = [c['display_str'] for c in citations]
            pages_display = ', '.join(disp_citations)

            name_norm = normalize_for_search(name)
            notes_norm = normalize_for_search(notes)

            cur.execute('''
                INSERT INTO toponyms (
                    name, name_normalized, notes, notes_normalized,
                    volume, volume_id, pages_json, pages_display
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                name, name_norm, notes, notes_norm,
                vol_name, vol_id, json.dumps(citations), pages_display))

            toponym_id = cur.lastrowid
            total_toponyms += 1

            for c in citations:
                cur.execute('''
                    INSERT INTO toponym_pages (
                        toponym_id, volume_id, page_start, page_end,
                        page_str, suffix, commentary, is_main,
                        target_page, display_str, seq
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    toponym_id, vol_id, c['page_start'], c['page_end'],
                    c['page_str'], c['suffix'], c['commentary'],
                    1 if c['is_main'] else 0, c['target_page'],
                    c['display_str'], c['seq']))
                total_pages += 1

    # Populate FTS5 index
    print('Building FTS5 index...')
    cur.execute('''
        INSERT INTO toponyms_fts(
            rowid, name, name_normalized, notes, notes_normalized,
            pages_display, volume
        ) SELECT id, name, name_normalized, notes, notes_normalized,
                 pages_display, volume FROM toponyms;
    ''')

    conn.commit()
    conn.close()

    db_size = os.path.getsize(target_db_path) / 1024 / 1024
    print(f'Done! Successfully indexed {total_toponyms} toponyms and '
          f'{total_pages} page citations. Database size: {db_size:.2f} MB')


if __name__ == '__main__':
    SOURCE_DIR = '/home/bkoschicek/www/tib/tib/data/register'
    TARGET_DB = '/home/bkoschicek/www/maps-of-power/mop/data/tib_register.db'
    build_database(SOURCE_DIR, TARGET_DB)
