"""TIB database access and search services.

Provides query methods for the Tabula Imperii Byzantini (TIB) SQLite
register, including diacritic-tolerant and Greek homoglyph search.
"""

from functools import lru_cache
import json
from pathlib import Path
import re
import sqlite3
from typing import Any
import unicodedata

DB_PATH = (
    Path(__file__).resolve().parent.parent / 'data' / 'tib_register.db')

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

VOLUMES_INFO: list[dict[str, Any]] = [
    {'id': 1, 'key': 'tib1', 'name': 'TIB 1',
     'title': 'TIB 1 Hellas and Thessaly',
     'authors': 'Johannes Koder, Friedrich Hild',
     'published': True, 'has_reader': True, 'pages': 315},
    {'id': 2, 'key': 'tib2', 'name': 'TIB 2',
     'title': 'TIB 2 Cappadocia',
     'authors': 'Friedrich Hild, Marcell Restle',
     'published': True, 'has_reader': True, 'pages': 339},
    {'id': 3, 'key': 'tib3', 'name': 'TIB 3',
     'title': 'TIB 3 Nicopolis and Cephalonia',
     'authors': 'Peter Soustal, Johannes Koder',
     'published': True, 'has_reader': True, 'pages': 326},
    {'id': 4, 'key': 'tib4', 'name': 'TIB 4',
     'title': 'TIB 4 Galatia and Lycaonia',
     'authors': 'Klaus Belke, Marcell Restle',
     'published': True, 'has_reader': True, 'pages': 305},
    {'id': 5, 'key': 'tib5', 'name': 'TIB 5',
     'title': 'TIB 5 Cilicia and Isauria',
     'authors': 'Friedrich Hild, Hansgerd Hellenkemper',
     'published': True, 'has_reader': True, 'pages': 467},
    {'id': 6, 'key': 'tib6', 'name': 'TIB 6',
     'title': 'TIB 6 Thrace',
     'authors': 'Peter Soustal',
     'published': True, 'has_reader': True, 'pages': 583},
    {'id': 7, 'key': 'tib7', 'name': 'TIB 7',
     'title': 'TIB 7 Phrygia and Pisidia',
     'authors': 'Klaus Belke, Norbert Mersich',
     'published': True, 'has_reader': True, 'pages': 463},
    {'id': 8, 'key': 'tib8', 'name': 'TIB 8',
     'title': 'TIB 8 Lycia and Pamphylia',
     'authors': 'Friedrich Hild, Hansgerd Hellenkemper',
     'published': True, 'has_reader': False, 'pages': 0},
    {'id': 9, 'key': 'tib9', 'name': 'TIB 9',
     'title': 'TIB 9 Paphlagonia and Honorias',
     'authors': 'Klaus Belke',
     'published': True, 'has_reader': False, 'pages': 0},
    {'id': 10, 'key': 'tib10', 'name': 'TIB 10',
     'title': 'TIB 10 Northern Aegean',
     'authors': 'Johannes Koder',
     'published': True, 'has_reader': False, 'pages': 0},
    {'id': 11, 'key': 'tib11', 'name': 'TIB 11',
     'title': 'TIB 11 Macedonia, Southern Part',
     'authors': 'Peter Soustal',
     'published': True, 'has_reader': False, 'pages': 0},
    {'id': 12, 'key': 'tib12', 'name': 'TIB 12',
     'title': 'TIB 12 Eastern Thrace (Eurōpē)',
     'authors': 'Andreas Külzer',
     'published': True, 'has_reader': True, 'pages': 860},
    {'id': 13, 'key': 'tib13', 'name': 'TIB 13',
     'title': 'TIB 13 Bithynia and Hellespont',
     'authors': 'Klaus Belke',
     'published': True, 'has_reader': True, 'pages': 1367},
    {'id': 14, 'key': 'tib14', 'name': 'TIB 14',
     'title': 'TIB 14 Western Asia Minor: Lydia and Asia',
     'authors': 'Peter Soustal',
     'published': False, 'has_reader': False, 'pages': 0},
    {'id': 15, 'key': 'tib15', 'name': 'TIB 15',
     'title': 'TIB 15 Syria',
     'authors': 'Friedrich Hild',
     'published': True, 'has_reader': False, 'pages': 0},
    {'id': 16, 'key': 'tib16', 'name': 'TIB 16',
     'title': 'TIB 16 Macedonia, Northern Part',
     'authors': 'Mihailo Popović',
     'published': False, 'has_reader': False, 'pages': 0},
    {'id': 17, 'key': 'tib17', 'name': 'TIB 17',
     'title': 'TIB 17 Nea Epeiros and Praevalis',
     'authors': 'Andreas Külzer',
     'published': False, 'has_reader': False, 'pages': 0},
    {'id': 18, 'key': 'tib18', 'name': 'TIB 18',
     'title': 'TIB 18 Caria',
     'authors': 'Friedrich Hild',
     'published': False, 'has_reader': False, 'pages': 0}]


def get_db_connection() -> sqlite3.Connection:
    """Return a read-only SQLite connection to the TIB register."""
    db_uri = f'file:{DB_PATH.as_posix()}?mode=ro'
    conn = sqlite3.connect(db_uri, uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def normalize_search_term(text: str) -> str:
    """Convert search queries to diacritic-folded Latin representation."""
    if not text:
        return ''
    chars = [GREEK_TO_LATIN.get(c, c) for c in text]
    s = ''.join(chars)
    decomposed = unicodedata.normalize('NFKD', s)
    stripped = ''.join(c for c in decomposed if not unicodedata.combining(c))
    return stripped.replace('ß', 'ss').lower().strip()


@lru_cache(maxsize=1)
def get_volume_counts() -> dict[int, int]:
    """Return dictionary of volume_id to total toponym count."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            'SELECT volume_id, COUNT(*) as cnt '
            'FROM toponyms GROUP BY volume_id')
        counts = {row['volume_id']: row['cnt'] for row in cur.fetchall()}
        conn.close()
        return counts
    except sqlite3.Error:
        return {}


def get_volume_metadata() -> list[dict[str, Any]]:
    """Return list of volume metadata enriched with actual record counts."""
    counts = get_volume_counts()
    volumes = []
    for vol in VOLUMES_INFO:
        cnt = counts.get(vol['id'], 0)
        v = dict(vol)
        v['toponym_count'] = cnt
        volumes.append(v)
    return volumes


# pylint: disable=too-many-locals
def search_toponyms(
        query: str = '',
        volume_id: int | None = None,
        limit: int = 50,
        offset: int = 0) -> dict[str, Any]:
    """Search toponyms by query and optional volume filter."""
    clean_q = query.strip()
    norm_q = normalize_search_term(clean_q)

    conn = get_db_connection()
    cur = conn.cursor()

    params: list[Any] = []
    where_clauses: list[str] = []

    if volume_id:
        where_clauses.append('t.volume_id = ?')
        params.append(volume_id)

    if norm_q:
        # FTS5 search expression with prefix wildcard
        # Sanitize query for FTS5 (remove special punctuation)
        safe_q = re.sub(r'[\'\"*^\-:()]', ' ', norm_q).strip()
        terms = [f'"{t}"*' for t in safe_q.split() if t]
        fts_expr = ' '.join(terms) if terms else f'"{norm_q}"*'

        fts_sql = '''
            t.id IN (
                SELECT rowid FROM toponyms_fts
                WHERE toponyms_fts MATCH ?
            )
        '''
        where_clauses.append(fts_sql)
        params.append(fts_expr)

    where_str = (
        'WHERE ' + ' AND '.join(where_clauses)
    ) if where_clauses else ''

    # Count total matching rows
    count_sql = f'SELECT COUNT(*) as total FROM toponyms t {where_str}'
    cur.execute(count_sql, params)
    total = cur.fetchone()['total']

    # Fetch paginated results
    select_sql = f'''
        SELECT t.id, t.name, t.notes, t.volume, t.volume_id,
               t.pages_json, t.pages_display
        FROM toponyms t
        {where_str}
        ORDER BY t.volume_id ASC, t.name COLLATE NOCASE ASC
        LIMIT ? OFFSET ?
    '''
    cur.execute(select_sql, params + [limit, offset])

    results = []
    for row in cur.fetchall():
        try:
            pages = json.loads(row['pages_json'])
        except (json.JSONDecodeError, TypeError):
            pages = []

        results.append({
            'id': row['id'],
            'name': row['name'],
            'notes': row['notes'],
            'volume': row['volume'],
            'volume_id': row['volume_id'],
            'pages': pages,
            'pages_display': row['pages_display']})

    conn.close()
    return {'total': total, 'limit': limit, 'offset': offset,
            'results': results}


def get_reader_pages(volume_key: str) -> list[dict[str, Any]]:
    """Return list of page image items for the book reader."""
    clean_key = volume_key.lower().replace(' ', '')
    vol = next((v for v in VOLUMES_INFO if v['key'] == clean_key), None)
    if not vol or not vol['has_reader']:
        return []

    num_pages = vol['pages']
    vol_num = vol['id']
    base_url = f'/static/repository/books/{clean_key}/'

    pages = []
    for i in range(1, num_pages + 1):
        filename = f'TIB{vol_num}_Seite_{i:03d}.jpg'
        pages.append({
            'page_num': i,
            'filename': filename,
            'url': f'{base_url}{filename}',
            'label': f'Page {i}'})

    return pages
