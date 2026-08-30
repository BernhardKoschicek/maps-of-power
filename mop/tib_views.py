"""Views and API endpoints for Tabula Imperii Byzantini (TIB).

Provides the TIB volume overview, interactive register table, modern book
reader, and search API endpoints.
"""

from typing import Any

from flask import abort, jsonify, render_template, request
from flask_babel import lazy_gettext as _

from mop import app
from mop.model.tib_db import (
    get_reader_pages, get_volume_metadata, search_toponyms, VOLUMES_INFO)


@app.route('/tib')
def tib_overview() -> str:
    """Render the TIB overview hub with cards for volumes 1-18."""
    volumes = get_volume_metadata()
    total_toponyms = sum(v.get('toponym_count', 0) for v in volumes)
    total_scans = sum(1 for v in volumes if v.get('has_reader'))
    return render_template(
        'tib/overview.html',
        volumes=volumes,
        total_toponyms=total_toponyms,
        total_scans=total_scans)


@app.route('/tib/register')
@app.route('/tib/register/<volume_key>')
def tib_register(volume_key: str | None = None) -> str:
    """Render the interactive TIB register table."""
    selected_key = volume_key.lower() if volume_key else 'all'
    volumes = get_volume_metadata()

    active_vol = None
    if selected_key != 'all':
        active_vol = next(
            (v for v in volumes if v['key'] == selected_key), None)
        if not active_vol:
            abort(404)

    return render_template(
        'tib/register.html',
        volumes=volumes,
        active_vol=active_vol,
        selected_key=selected_key)


@app.route('/tib/reader/<volume_key>')
def tib_reader(volume_key: str) -> str:
    """Render the modern HTML5 book reader for a specific volume."""
    clean_key = volume_key.lower()
    volumes = get_volume_metadata()
    vol = next((v for v in volumes if v['key'] == clean_key), None)

    if not vol or not vol.get('has_reader'):
        abort(404)

    pages = get_reader_pages(clean_key)
    initial_page = request.args.get('page', default=1, type=int)

    return render_template(
        'tib/reader.html',
        volume=vol,
        volumes=volumes,
        pages=pages,
        initial_page=initial_page)


@app.route('/api/tib/search')
def api_tib_search() -> Any:
    """Search endpoint for TIB toponyms with diacritic tolerance."""
    q = request.args.get('q', default='', type=str).strip()
    volume_param = request.args.get('volume', default='', type=str).strip()
    limit = min(request.args.get('limit', default=50, type=int), 200)
    offset = max(request.args.get('offset', default=0, type=int), 0)

    volume_id: int | None = None
    if volume_param and volume_param != 'all':
        if volume_param.isdigit():
            volume_id = int(volume_param)
        else:
            vol_match = next(
                (v for v in VOLUMES_INFO
                 if v['key'] == volume_param.lower()), None)
            if vol_match:
                volume_id = vol_match['id']

    result = search_toponyms(
        query=q,
        volume_id=volume_id,
        limit=limit,
        offset=offset)

    return jsonify({
        'query': q,
        'volume_id': volume_id,
        'total': result['total'],
        'limit': result['limit'],
        'offset': result['offset'],
        'results': result['results']})


@app.route('/api/tib/reader/<volume_key>/pages')
def api_tib_reader_pages(volume_key: str) -> Any:
    """Return list of page image objects for book reader viewer."""
    pages = get_reader_pages(volume_key)
    if not pages:
        return jsonify(
            {'error': 'Volume has no reader scans', 'code': 404}), 404

    return jsonify({
        'volume': volume_key,
        'total_pages': len(pages),
        'pages': pages})
