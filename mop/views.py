from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, cast
from urllib.parse import urlsplit

from flask import (
    Blueprint, Flask, abort, current_app, jsonify, render_template, request,
    send_from_directory, session, url_for)
from flask_babel import lazy_gettext as _
from werkzeug import Response
from werkzeug.exceptions import HTTPException
from werkzeug.utils import redirect

from mop.extensions import cache, get_app_config
from mop.data.events import event_list
from mop.data.histgeo import lectures, newsletters, volumes
from mop.data.images import category_images
from mop.data.literature import literatures
from mop.data.presentations import presentations
from mop.data.projects.projects import project_data
from mop.display.image import image_gallery
from mop.display.thumbnail import ensure_thumbnail
from mop.model.api_calls import (
    fetch_table_rows as _fetch_table_rows,
    fetch_table_rows_count as _fetch_table_rows_count,
    fetch_table_rows_uncached as _fetch_table_rows_uncached,
    get_ego_network, get_network_visualisation)
from mop.model.entity import Entity
from mop.model.explore import (
    get_oa_by_view_class, system_classes, view_classes)
from mop.model.narrative import NarrativeGenerator
from mop.model.presentation import (
    build_entity_timeline, prepare_entity_geometries)
from mop.util import (
    array_split, get_dict_entries_by_category, get_types_sorted)

main_bp = Blueprint('main', __name__)
explore_bp = Blueprint('explore', __name__)


def get_project_api_path(project_acronym: str | None) -> str:
    if project_acronym and project_acronym in project_data:
        api_type = project_data[project_acronym].get('api')
        if api_type == 'ortho':
            return get_app_config('ORTHO_API_PATH', '')
    return get_app_config('MOP_API_PATH', '')



@main_bp.route('/')
def about() -> str:
    has_video = (_get_media_folder() / 'videos' / 'hero.mp4').exists()
    return render_template(
        'about.html',
        category_images=image_gallery(category_images),
        events=event_list,
        has_local_hero_video=has_video)


@main_bp.route('/events')
def events() -> str:
    return render_template('events.html', events=event_list)


@main_bp.route('/histgeo')
@main_bp.route('/histgeo/<int:id_>')
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


@main_bp.route('/imprint')
def imprint() -> str:
    return render_template('imprint.html')


@main_bp.route('/language=<language>')
def set_language(language: str | None = None) -> Response:
    allowed_languages = current_app.config.get('LANGUAGES', {})
    if language and language in allowed_languages:
        session['language'] = language
    target = url_for('main.about')
    if request.referrer:
        parsed_ref = urlsplit(request.referrer)
        allowed_hosts = {request.host}
        pub_url = str(get_app_config('PUBLIC_BASE_URL', '')).strip()
        if pub_url:
            pub_netloc = urlsplit(pub_url).netloc
            if pub_netloc:
                allowed_hosts.add(pub_netloc)
        path = parsed_ref.path or '/'
        if (parsed_ref.scheme in ('', 'http', 'https')
                and parsed_ref.netloc in ('', *allowed_hosts)
                and path.startswith('/')
                and not path.startswith('//')
                and '\\' not in path):
            target = (
                f"{path}?{parsed_ref.query}"
                if parsed_ref.query else path)
    return redirect(target)


@main_bp.route('/literature')
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
            'citation_text': citation_text,
            'type': lit.get('type', '')}
        processed_literatures.append(processed_lit)

    return render_template(
        'literature.html',
        literatures=processed_literatures,
        projects=project_data)


@explore_bp.route('/projects')
@explore_bp.route('/projects/<title>')
def projects(title: str | None = None) -> Response | str:
    if title:
        if title == 'tib':
            return redirect(url_for('tib.tib_overview'))
        if title not in project_data:
            abort(404)
        return render_template(
            'project_details.html',
            project=project_data[title],
            presentations=get_dict_entries_by_category(title, presentations),
            publications=get_dict_entries_by_category(title, literatures),
            view_classes=view_classes)
    portal_projects = {k: v for k, v in project_data.items() if k != 'tib'}
    return render_template('projects.html', projects=portal_projects)


@explore_bp.route('/projects/<project>/explore/<view>')
def project_explore_table(
        project: str | None = None,
        view: str | None = None) -> str | tuple[str, int]:
    if (not project or not view or project not in project_data
            or view not in view_classes):
        abort(404)
    data = []
    upstream_failed = False
    try:
        api_path = get_project_api_path(project)
        data = get_oa_by_view_class(
            view, project_data[project]['oaID'], api_path=api_path)
    except Exception as e:  # pragma: no cover
        upstream_failed = True
        current_app.logger.error("Error fetching open access data: %s", e)
    rendered = render_template(
        'explore/project_explore_table.html',
        data=data,
        project=project_data[project],
        view_classes=view_classes[view],
        view=view)
    if upstream_failed:
        return rendered, 503
    return rendered


@explore_bp.route('/entity/<int:id_>')
@explore_bp.route('/projects/<project>/explore/<view>/<int:id_>')
def entity_project_view(
        id_: int, project: str | None = None, view: str | None = None) -> str:
    if (project is not None
            and project not in project_data):  # pragma: no cover
        abort(404)
    if view is not None and view not in view_classes:  # pragma: no cover
        abort(404)
    api_path = get_project_api_path(project)
    entity = Entity.get_entity_from_oa(id_, api_path=api_path)
    relations = entity.relations or {}
    related_places = prepare_entity_geometries(entity, relations)
    timeline_events = build_entity_timeline(entity, relations)
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
        images=(array_split(cast(Any, entity.depictions), 4)
                if entity.depictions else None),
        relations=relations,
        related_places=related_places,
        timeline_events=timeline_events,
        path=(project, view),
        system_classes=system_classes,
        narratives=narratives,
        project_details=project_details,
        api_path=api_path)


@main_bp.route('/software')
def software() -> str:
    return render_template('software.html')


def _get_allowed_iiif_hosts() -> set[str]:
    hosts: set[str] = set()
    for cfg_key in (
            'MOP_API_PATH', 'ORTHO_API_PATH', 'OPENATLAS_API_BASE',
            'PUBLIC_BASE_URL'):
        val = str(get_app_config(cfg_key, '')).strip()
        if val:
            parsed = urlsplit(val)
            if parsed.hostname:
                hosts.add(parsed.hostname.lower())
    for extra in get_app_config('IIIF_ALLOWED_HOSTS', []) or []:
        if extra:
            hosts.add(str(extra).strip().lower())
    return hosts


@main_bp.route('/iiif_viewer')
def iiif_viewer() -> str:
    raw_manifest = (request.args.get('manifest') or '').strip()
    if not raw_manifest:
        abort(400)
    parsed = urlsplit(raw_manifest)
    if (parsed.scheme not in ('http', 'https')
            or not parsed.hostname
            or parsed.hostname.lower() not in _get_allowed_iiif_hosts()):
        abort(400)
    pub_base = str(get_app_config('PUBLIC_BASE_URL', '')).strip().rstrip('/')
    root_url = f"{pub_base}/" if pub_base else request.url_root
    sep = '&' if parsed.query else '?'
    manifest = f'{raw_manifest}{sep}url={root_url}entity/'
    return render_template('iiif_viewer.html', manifest=manifest)


@main_bp.route('/atlas')
@main_bp.route('/frontend')
def frontend() -> Response:
    return redirect("https://atlas.maps-of-power.at/")


DEFAULT_MEDIA_PATH = (
    Path(__file__).resolve().parent.parent / 'storage' / 'media')


def _get_media_folder() -> Path:
    configured = get_app_config('MEDIA_FOLDER', None)
    if configured:
        return Path(configured)
    return DEFAULT_MEDIA_PATH


@main_bp.route('/media/thumbnails/<path:filename>')
@main_bp.route('/static/thumbnails/<path:filename>')
def serve_legacy_thumbnails(filename: str) -> Response:
    media_folder = _get_media_folder()
    thumb = ensure_thumbnail(filename, media_folder)
    if thumb and thumb.exists():
        return send_from_directory(thumb.parent, thumb.name)
    return send_from_directory(media_folder / 'thumbnails', filename)


@main_bp.route('/media/<path:filename>')
def serve_media(filename: str) -> Response:
    media_folder = _get_media_folder()
    if filename.startswith('thumbnails/'):
        thumb_name = filename[len('thumbnails/'):]
        thumb = ensure_thumbnail(thumb_name, media_folder)
        if thumb and thumb.exists():
            return send_from_directory(thumb.parent, thumb.name)
    return send_from_directory(media_folder, filename)


@main_bp.route('/static/images/<path:filename>')
def serve_legacy_images(filename: str) -> Response:
    return send_from_directory(_get_media_folder() / 'images', filename)


@main_bp.route('/static/repository/books/<path:filename>')
def serve_legacy_books(filename: str) -> Response:
    return send_from_directory(_get_media_folder() / 'books', filename)


@main_bp.route('/static/repository/<path:filename>')
def serve_legacy_repository(filename: str) -> Response:
    return send_from_directory(_get_media_folder() / 'repository', filename)


@main_bp.route('/static/videos/<path:filename>')
def serve_legacy_videos(filename: str) -> Response:
    return send_from_directory(_get_media_folder() / 'videos', filename)


@explore_bp.route('/api/network/<int:id_>')
def network_api(id_: int) -> Response | tuple[Response, int]:
    depth = max(1, min(5, request.args.get('depth', default=2, type=int)))
    project = request.args.get('project')
    try:
        api_path = get_project_api_path(project)
        data = get_ego_network(id_, depth, api_path=api_path)
        return jsonify(data)
    except HTTPException:
        raise
    except Exception as e:
        current_app.logger.error("Error in network_api: %s", e)
        return jsonify({"error": "Internal server error"}), 500


@cache.memoize(timeout=3600)
def _get_cached_project_places(
        project_acronym: str,
        oa_ids: tuple[str, ...]) -> list[dict[str, Any]]:
    api_path = get_project_api_path(project_acronym)
    places = get_oa_by_view_class(
        'place', list(oa_ids), api_path=api_path)
    simplified: list[dict[str, Any]] = []
    for p in places:
        if p and p.geometry:
            simplified.append({
                'id': p.id_,
                'name': p.name,
                'system_class': p.system_class,
                'geometry': p.geometry,
                'description': (p.description or '')[:220],
                'project': project_acronym.upper()})
    return simplified


def _fetch_places_for_project(
        app_obj: Flask,
        acronym: str,
        oa_key: tuple[str, ...]) -> list[dict[str, Any]]:
    with app_obj.app_context():
        return _get_cached_project_places(acronym, oa_key)


@explore_bp.route('/api/places/<project_acronym>')
def api_project_places(
        project_acronym: str) -> Response | tuple[Response, int]:
    if project_acronym == 'all':
        try:
            targets: list[tuple[str, tuple[str, ...]]] = []
            for acronym, proj in project_data.items():
                if acronym == 'tib':
                    continue
                oa_id = proj.get('oaID')
                if not oa_id:
                    continue
                oa_key = (
                    tuple(str(x) for x in oa_id)
                    if isinstance(oa_id, list) else (str(oa_id),))
                targets.append((acronym, oa_key))
            combined: list[dict[str, Any]] = []
            if targets:
                app_obj = cast(
                    Flask,
                    cast(Any, current_app)._get_current_object())  # pylint: disable=W0212
                with ThreadPoolExecutor(max_workers=4) as executor:
                    futures = [
                        executor.submit(
                            _fetch_places_for_project, app_obj, acr, key)
                        for acr, key in targets]
                    for fut in futures:
                        combined.extend(fut.result())
            return jsonify({'places': combined})
        except Exception as e:
            current_app.logger.error("Error in api_project_places: %s", e)
            return jsonify({"error": "Internal server error"}), 500

    if project_acronym not in project_data:
        return jsonify({'error': 'Project not found'}), 404
    oa_id = project_data[project_acronym].get('oaID')
    if not oa_id:
        return jsonify({'places': []})
    oa_key = (
        tuple(str(x) for x in oa_id)
        if isinstance(oa_id, list) else (str(oa_id),))
    try:
        simplified = _get_cached_project_places(project_acronym, oa_key)
        return jsonify({'places': simplified})
    except Exception as e:
        current_app.logger.error("Error in api_project_places: %s", e)
        return jsonify({"error": "Internal server error"}), 500


# pylint: disable=too-many-return-statements
@explore_bp.route('/api/network/project/<project_acronym>')
def api_project_network(
        project_acronym: str) -> Response | tuple[Response, int]:
    if project_acronym == "all":
        mop_ids = []
        ortho_ids = []
        for proj in project_data.values():
            oa_id = proj.get('oaID')
            if not oa_id:
                continue
            ids_to_add = [
                int(x)
                for x in (oa_id if isinstance(oa_id, list) else [oa_id])
                if str(x).isdigit()]
            if proj.get('api') == 'ortho':
                ortho_ids.extend(ids_to_add)
            else:
                mop_ids.extend(ids_to_add)

        try:
            mop_res = (
                get_network_visualisation(
                    mop_ids, api_path=get_project_api_path('mop'))
                if mop_ids else {'results': []})
            ortho_res = (
                get_network_visualisation(
                    ortho_ids, api_path=get_project_api_path('rhr'))
                if ortho_ids else {'results': []})
            combined_results = (
                mop_res.get('results', []) + ortho_res.get('results', []))
            return jsonify({'results': combined_results})
        except Exception as e:
            current_app.logger.error("Error in api_project_network: %s", e)
            return jsonify({"error": "Internal server error"}), 500
    else:
        if project_acronym not in project_data:
            return jsonify({'error': 'Project not found'}), 404
        oa_id = project_data[project_acronym].get('oaID')
        if not oa_id:
            return jsonify({'results': []})
        linked_to_ids = [
            int(x)
            for x in (oa_id if isinstance(oa_id, list) else [oa_id])
            if str(x).isdigit()]
        if not linked_to_ids:
            return jsonify({'results': []})
        try:
            api_path = get_project_api_path(project_acronym)
            data = get_network_visualisation(linked_to_ids, api_path=api_path)
            return jsonify(data)
        except Exception as e:
            current_app.logger.error("Error in api_project_network: %s", e)
            return jsonify({"error": "Internal server error"}), 500


ALLOWED_TABLE_COLUMNS = {
    'begin', 'class', 'description', 'end', 'name', 'type'}
ALLOWED_SORT_DIRECTIONS = {'asc', 'desc'}


@explore_bp.route('/api/explore/<project_acronym>/<view>')
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
    page = max(1, min(request.args.get('page', 1, type=int), 10000))
    raw_sort = request.args.get('sort', 'asc').lower()
    sort = raw_sort if raw_sort in ALLOWED_SORT_DIRECTIONS else 'asc'
    raw_col = request.args.get('column', 'name').lower()
    column = raw_col if raw_col in ALLOWED_TABLE_COLUMNS else 'name'
    search = request.args.get('search', '').strip()[:100]
    try:
        api_path = get_project_api_path(project_acronym)
        if search:
            data = _fetch_table_rows_uncached(
                view, oa_ids, page, sort, column, search, api_path=api_path)
        else:
            data = _fetch_table_rows(
                view, oa_ids, page, sort, column, search, api_path=api_path)
        return jsonify(data)
    except Exception as e:
        current_app.logger.error("Error in api_explore_entities: %s", e)
        return jsonify({'error': 'Internal server error'}), 500


@explore_bp.route('/api/explore/<project_acronym>/<view>/count')
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
        api_path = get_project_api_path(project_acronym)
        count = _fetch_table_rows_count(view, oa_ids, api_path=api_path)
        return jsonify({'count': count})
    except Exception as e:
        current_app.logger.error("Error in api_explore_count: %s", e)
        return jsonify({'error': 'Internal server error', 'count': 0}), 500


@main_bp.route('/health')
def health() -> Response:
    return jsonify({
        'status': 'ok',
        'version': get_app_config('VERSION', '0.1.0')})


@main_bp.app_errorhandler(HTTPException)
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


@main_bp.app_errorhandler(Exception)
def handle_generic_exception(
        e: Exception
) -> (Response | tuple[str, int] | tuple[Response, int]):  # pragma: no cover
    if isinstance(e, HTTPException):
        return handle_http_exception(e)

    current_app.logger.error("Unhandled exception: %s", e, exc_info=True)

    if request.path.startswith('/api/'):
        return jsonify({
            'error': _('Internal Server Error'), 'code': 500}), 500

    return render_template(
        'error.html',
        code=500,
        title=_("Internal Server Error"),
        description=_(
            "An unexpected server error occurred. "
            "Our cartographers are looking into it.")), 500
