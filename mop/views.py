import json
import re
from typing import Any, cast

import numpy
import requests
from flask import abort, jsonify, render_template, request, session
from flask_babel import lazy_gettext as _
from werkzeug import Response
from werkzeug.exceptions import HTTPException
from werkzeug.utils import redirect

from mop import app, cache
from mop.data.events import event_list
from mop.data.histgeo import lectures, newsletters, volumes
from mop.data.images import category_images
from mop.data.literature import literatures
from mop.data.presentations import presentations
from mop.data.projects.projects import project_data
from mop.display.image import image_gallery
from mop.model.api_calls import get_ego_network, get_network_visualisation
from mop.model.entity import Entity
from mop.model.explore import (
    get_oa_by_view_class, system_classes, view_classes)
from mop.model.narrative import NarrativeGenerator
from mop.util import get_dict_entries_by_category, get_types_sorted


@app.route('/')
def about() -> str:
    return render_template(
        'about.html',
        category_images=image_gallery(category_images),
        events=event_list)


@app.route('/events')
def events() -> str:
    return render_template('events.html', events=event_list)


@app.route('/histgeo')
@app.route('/histgeo/<int:id_>')
def histgeo(id_: int | None = None) -> str:
    if id_:
        if id_ not in lectures:
            abort(404)
        return render_template('lectures.html', lecture=lectures[id_])
    return render_template(
        'histgeo.html',
        lectures=lectures,
        newsletters=newsletters,
        volumes=volumes)


@app.route('/imprint')
def imprint() -> str:
    return render_template('imprint.html')


@app.route('/language=<language>')
def set_language(language: str | None = None) -> Response:
    session['language'] = language
    return redirect(request.referrer)


@app.route('/literature')
def literature() -> str:
    processed_literatures = []
    for lit in literatures:
        # Pre-process categories
        cats = lit.get('category', [])
        norm_cats = []
        for c in cats:
            if c in project_data:
                norm_cats.append(c)
        if not norm_cats:
            norm_cats.append('further')

        # Pre-render citation string: Author, Title. Location, Year. pp. Pages.
        author = lit.get('author', '').strip()
        title = lit.get('title', '').strip()

        # Form location string
        locs = lit.get('locations', [])
        if isinstance(locs, list):
            loc_str = ', '.join(str(loc) for loc in locs if loc)
        elif locs:
            loc_str = str(locs)
        else:
            loc_str = ''

        date = lit.get('date', '').strip()
        pages = lit.get('pages', '').strip()

        citation_parts = []
        if author:
            citation_parts.append(author)
        if title:
            citation_parts.append(f'"{title.rstrip(".")}"')
        if loc_str:
            citation_parts.append(loc_str)
        if date:
            citation_parts.append(date)
        if pages:
            citation_parts.append(f'{_("pp.")} {pages}')

        citation_text = ', '.join(citation_parts) + '.'

        processed_lit = {
            'author': lit.get('author', ''),
            'title': lit.get('title', ''),
            'locations': lit.get('locations', []),
            'date': lit.get('date', ''),
            'pages': lit.get('pages', ''),
            'external_link': lit.get('external_link', ''),
            'download': lit.get('download', ''),
            'categories': norm_cats,
            'citation_text': citation_text}
        processed_literatures.append(processed_lit)

    return render_template(
        'literature.html',
        literatures=processed_literatures,
        projects=project_data)


@app.route('/projects')
@app.route('/projects/<title>')
def projects(title: str | None = None) -> str:
    if title:
        if title not in project_data:
            abort(404)
        return render_template(
            'project_details.html',
            project=project_data[title],
            presentations=get_dict_entries_by_category(title, presentations),
            publications=get_dict_entries_by_category(title, literatures),
            view_classes=view_classes)
    return render_template('projects.html', projects=project_data)


@app.route('/projects')
@app.route('/projects/<project>/explore/<view>')
def project_explore_table(project: str, view: str) -> str:
    if project not in project_data or view not in view_classes:
        abort(404)
    data = []
    try:
        data = get_oa_by_view_class(view, project_data[project]['oaID'])
    except Exception as e:  # pragma: no cover
        app.logger.error("Error fetching open access data: %s", e)
    return render_template(
        'explore/project_explore_table.html',
        data=data,
        project=project_data[project],
        view_classes=view_classes[view],
        view=view)


@app.route('/projects')
@app.route('/entity/<int:id_>')
@app.route('/projects/<project>/explore/<view>/<int:id_>')
# pylint: disable=too-many-locals, too-many-branches, too-many-statements
def entity_project_view(
        id_: int, project: str | None = None, view: str | None = None) -> str:
    if (project is not None
            and project not in project_data):  # pragma: no cover
        abort(404)
    if view is not None and view not in view_classes:  # pragma: no cover
        abort(404)
    entity = Entity.get_entity_from_oa(id_)
    relations = entity.relations or {}

    def normalize_and_inject_geojson(
            geojson_obj: Any,
            properties: dict[str, Any]) -> list[dict[str, Any]]:
        if not geojson_obj:  # pragma: no cover
            return []
        if not isinstance(geojson_obj, dict):  # pragma: no cover
            return []
        obj_type = geojson_obj.get('type')
        features = []
        if obj_type == 'FeatureCollection':
            for f in geojson_obj.get('features', []):
                if isinstance(f, dict):  # pragma: no cover
                    f_copy = dict(f)
                    f_copy['properties'] = dict(f_copy.get('properties') or {})
                    for k, v in properties.items():
                        f_copy['properties'][k] = v
                    features.append(f_copy)
        elif obj_type == 'Feature':
            f_copy = dict(geojson_obj)
            f_copy['properties'] = dict(f_copy.get('properties') or {})
            for k, v in properties.items():
                f_copy['properties'][k] = v
            features.append(f_copy)
        elif obj_type in {'Point', 'MultiPoint', 'LineString',
                          'MultiLineString', 'Polygon', 'MultiPolygon',
                          'GeometryCollection'}:
            features.append({
                "type": "Feature",
                "geometry": geojson_obj,
                "properties": dict(properties)})
        return features

    # Standardize main entity geometry
    main_geometry = None
    if entity.geometry:  # pragma: no cover
        features = normalize_and_inject_geojson(
            entity.geometry, {
                "title": entity.name,
                "description": entity.description or "",
                "systemClass": "selected",
                "id": entity.id_})
        if features:
            main_geometry = {"type": "FeatureCollection", "features": features}
    entity.geometry = main_geometry

    # Standardize related entity geometries
    related_places = []
    seen_ids = set()
    for rel_group, rel_list in relations.items():
        for rel in rel_list:
            if rel.geometry and rel.relation_to_id not in seen_ids:
                seen_ids.add(rel.relation_to_id)
                features = normalize_and_inject_geojson(
                    rel.geometry, {
                        "title": rel.label,
                        "description": rel.description or "",
                        "systemClass": rel.system_class,
                        "id": rel.relation_to_id})
                related_places.extend(features)

    # Gather and sort all timeline events
    timeline_events = []
    for rel_group, rel_list in relations.items():
        if rel_group in ['references', 'sources', 'source_translations',
                         'others']:
            continue
        for rel in rel_list:
            if rel.begin:
                sort_date = rel.raw_begin or rel.begin
                timeline_events.append({
                    "is_main": False,
                    "relation": rel,
                    "sort_date": sort_date,
                    "category": rel_group})

    if entity.begin:  # pragma: no cover
        timeline_events.append({
            "is_main": True,
            "label": f"Start of {entity.name}",
            "type": "Lifecycle Start",
            "begin": entity.begin,
            "sort_date": entity.begin_from or entity.begin,
            "system_class": entity.system_class})
    if entity.end:  # pragma: no cover
        timeline_events.append({
            "is_main": True,
            "label": f"End of {entity.name}",
            "type": "Lifecycle End",
            "begin": entity.end,
            "sort_date": entity.end_from or entity.end,
            "system_class": entity.system_class})

    timeline_events.sort(key=lambda x: str(x['sort_date'] or ''))

    narratives = NarrativeGenerator.generate(
        entity, project=project, view=view)

    project_details = project_data.get(project) if project else None
    if project_details and not project_details.get('pi'):
        project_details = dict(project_details)
        project_details['pi'] = ['Mihailo Popović']

    return render_template(
        'explore/project_entity_view.html',
        entity=entity,
        type_hierarchy=get_types_sorted(entity.types or []),
        images=(numpy.array_split(cast(Any, entity.depictions), 4)
                if entity.depictions else None),
        relations=relations,
        related_places=related_places,
        timeline_events=timeline_events,
        path=(project, view),
        system_classes=system_classes,
        narratives=narratives,
        project_details=project_details)


@app.route('/software')
def software() -> str:
    return render_template('software.html')


@app.route('/iiif_viewer')
def iiif_viewer() -> str:
    manifest = request.args.get('manifest')
    manifest = f'{manifest}?url={request.url_root}entity/'
    return render_template('iiif_viewer.html', manifest=manifest)


@app.route('/atlas')
@app.route('/frontend')
def frontend() -> Response:
    return redirect("https://atlas.maps-of-power.at/")


@app.route('/api/network/<int:id_>')
def network_api(id_: int) -> Response | tuple[Response, int]:
    depth = request.args.get('depth', default=2, type=int)
    try:
        data = get_ego_network(id_, depth)
        return jsonify(data)
    except HTTPException:
        raise
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/places/<project_acronym>')
def api_project_places(
        project_acronym: str) -> Response | tuple[Response, int]:
    if project_acronym not in project_data:
        return jsonify({'error': 'Project not found'}), 404
    oa_id = project_data[project_acronym].get('oaID')
    if not oa_id:
        return jsonify({'places': []})
    try:
        places = get_oa_by_view_class('place', oa_id)
        simplified = []
        for p in places:
            if p and p.geometry:
                simplified.append({
                    'id': p.id_,
                    'name': p.name,
                    'system_class': p.system_class,
                    'geometry': p.geometry,
                    'description': p.description or ''})
        return jsonify({'places': simplified})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/network/project/<project_acronym>')
def api_project_network(
        project_acronym: str) -> Response | tuple[Response, int]:
    if project_acronym == "all":
        linked_to_ids = []
        for proj in project_data.values():
            oa_id = proj.get('oaID')
            if oa_id:
                linked_to_ids.extend([
                    int(x) for x in oa_id if str(x).isdigit()])
    else:
        if project_acronym not in project_data:
            return jsonify({'error': 'Project not found'}), 404
        oa_id = project_data[project_acronym].get('oaID')
        if not oa_id:
            return jsonify({'results': []})
        linked_to_ids = [int(x) for x in oa_id if str(x).isdigit()]

    if not linked_to_ids:
        return jsonify({'results': []})
    try:
        data = get_network_visualisation(linked_to_ids)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# pylint: disable=too-many-arguments, too-many-positional-arguments
@cache.memoize(timeout=3600)
def _fetch_table_rows(
        view: str, oa_ids: tuple[str, ...], page: int, sort: str, column: str,
        search: str) -> dict[str, Any]:
    """Proxy call to OpenAtlas /table_rows/ — cached server-side."""
    url = f"{app.config['API_PATH']}0.4/table_rows/"
    params: dict[str, Any] = {
        'view_classes': view,
        'sort': sort,
        'column': column,
        'page': page,
        'table_columns': [
            'begin', 'class', 'description', 'end', 'name', 'type'],
        'type_id': list(oa_ids), }
    if search:
        params['search'] = json.dumps({
            'entityName': [{
                'operator': 'like',
                'values': [search],
                'logicalOperator': 'and'}]})
    response = requests.get(
        url, params=params, proxies=get_proxies(), timeout=30)
    response.raise_for_status()
    data = response.json()
    rows = []
    for row in data.get('results', []):
        if not isinstance(row, list) or len(row) < 6:
            continue
        m = re.search(r'\bid="(\d+)"', str(row[0]))
        if not m:
            continue
        rows.append({
            'id': int(m.group(1)),
            'begin': row[1] or '',
            'class_': row[2] or '',
            'description': row[3] or '',
            'end': row[4] or '',
            'name': row[5] or '',
            'type': row[6] if len(row) > 6 else '', })
    return {'results': rows, 'pagination': data.get('pagination', {})}


@cache.memoize(timeout=3600)
def _fetch_table_rows_count(view: str, oa_ids: tuple[str, ...]) -> int:
    url = f"{app.config['API_PATH']}0.4/table_rows/"
    params: dict[str, Any] = {
        'view_classes': view,
        'count': 'true',
        'type_id': list(oa_ids), }
    response = requests.get(
        url, params=params, proxies=get_proxies(), timeout=30)
    response.raise_for_status()
    try:
        return int(response.text.strip())
    except ValueError:
        return 0


def _get_proxies() -> dict[str, str] | None:
    """Alias to avoid import conflict with the module-level helper."""
    proxy = app.config.get('API_PROXY')
    if not proxy:
        return None
    return {'http': proxy, 'https': proxy}  # pragma: no cover


def get_proxies() -> dict[str, str] | None:
    return _get_proxies()


@app.route('/api/explore/<project_acronym>/<view>')
def api_explore_entities(
        project_acronym: str,
        view: str) -> Response | tuple[Response, int]:
    if project_acronym not in project_data or view not in view_classes:
        return jsonify({'error': 'Not found'}), 404
    oa_id = project_data[project_acronym].get('oaID')
    if not oa_id:
        return jsonify({'results': [], 'pagination': {}})
    oa_ids: tuple[str, ...] = (
        tuple(oa_id) if isinstance(oa_id, list) else (str(oa_id),))
    page = request.args.get('page', 1, type=int)
    sort = request.args.get('sort', 'asc')
    column = request.args.get('column', 'name')
    search = request.args.get('search', '').strip()
    try:
        data = _fetch_table_rows(view, oa_ids, page, sort, column, search)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/explore/<project_acronym>/<view>/count')
def api_explore_count(
        project_acronym: str,
        view: str) -> Response | tuple[Response, int]:
    if project_acronym not in project_data or view not in view_classes:
        return jsonify({'count': 0}), 404
    oa_id = project_data[project_acronym].get('oaID')
    if not oa_id:
        return jsonify({'count': 0})
    oa_ids: tuple[str, ...] = (
        tuple(oa_id) if isinstance(oa_id, list) else (str(oa_id),))
    try:
        count = _fetch_table_rows_count(view, oa_ids)
        return jsonify({'count': count})
    except Exception as e:
        return jsonify({'error': str(e), 'count': 0}), 500


@app.errorhandler(HTTPException)
def handle_http_exception(
        e: HTTPException) -> tuple[Response, int] | tuple[str, int]:
    if request.path.startswith('/api/'):
        code = e.code or 500
        return jsonify({'error': e.description, 'code': code}), code

    code = e.code or 500
    title = e.name or _("An error occurred")
    description = e.description or _(
        "An unexpected error occurred. Please try again later.")

    if code == 404:
        title = _("Page Not Found")
        description = _(
            "The coordinates you entered seem to be out of bounds. "
            "The page you are looking for does not exist.")
    elif code == 403:
        title = _("Access Denied")
        description = _(
            "You do not have permission to access this area. "
            "Restricted coordinates.")
    elif code == 418:
        title = _("I'm a Teapot")
        description = _(
            "The server refuses the attempt to brew coffee with a teapot. "
            "Yes, this is a real error.")

    return render_template(
        'error.html', code=code, title=title, description=description), code


@app.errorhandler(Exception)
def handle_generic_exception(
        e: Exception
) -> (Response | tuple[str, int] | tuple[Response, int]):  # pragma: no cover
    if isinstance(e, HTTPException):
        return handle_http_exception(e)

    app.logger.error("Unhandled exception: %s", e, exc_info=True)

    if request.path.startswith('/api/'):
        return jsonify({'error': _('Internal Server Error'), 'code': 500}), 500

    return render_template(
        'error.html',
        code=500,
        title=_("Internal Server Error"),
        description=_(
            "An unexpected server error occurred. "
            "Our cartographers are looking into it.")), 500
