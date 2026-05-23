from collections import defaultdict
from typing import Literal, Optional

import numpy
from flask import abort, jsonify, render_template, request, session
from flask_babel import lazy_gettext as _
from werkzeug import Response
from werkzeug.exceptions import HTTPException
from werkzeug.utils import redirect

from mop import app
from mop.data.events import event_list
from mop.data.histgeo import lectures, newsletters, volumes
from mop.data.images import category_images
from mop.data.literature import literatures
from mop.data.presentations import presentations
from mop.data.projects.projects import project_data
from mop.display.image import image_gallery
from mop.model.api_calls import get_ego_network, get_entities_linked_to_entity
from mop.model.entity import Entity
from mop.model.explore import (get_oa_by_view_class, system_classes,
                               view_classes)
from mop.util import (get_dict_entries_by_category, get_related_geoms,
                      get_relation_entities, get_relations, get_types_sorted)


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
def histgeo(id_: Optional[int] = None) -> str:
    if id_:
        if id_ not in lectures:
            abort(404)
        return render_template(
            'lectures.html',
            lecture=lectures[id_])
    return render_template(
        'histgeo.html',
        lectures=lectures,
        newsletters=newsletters,
        volumes=volumes)


@app.route('/imprint')
def imprint() -> str:
    return render_template('imprint.html')


@app.route('/language=<language>')
def set_language(language: Optional[str] = None) -> Response:
    session['language'] = language
    return redirect(request.referrer)


@app.route('/literature')
def literature() -> str:
    literature_ = defaultdict(list)
    for lit in literatures:
        for cat in lit['category']:
            literature_[cat].append(lit)
    return render_template('literature.html', literatures=literature_)


@app.route('/projects')
@app.route('/projects/<title>')
def projects(title: Optional[str] = None) -> str:
    if title:
        if title not in project_data:
            abort(404)
        return render_template(
            'project_details.html',
            project=project_data[title],
            presentations=get_dict_entries_by_category(
                title,
                presentations),
            publications=get_dict_entries_by_category(
                title,
                literatures),
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
    except Exception:
        pass
    return render_template(
        'explore/project_explore_table.html',
        data=data,
        project=project_data[project],
        view_classes=view_classes[view],
        view=view)


@app.route('/projects')
@app.route('/entity/<int:id_>')
@app.route('/projects/<project>/explore/<view>/<int:id_>')
def entity_project_view(
        id_: int,
        project: Optional[str] = None,
        view: Optional[str] = None) -> str:
    if project is not None and project not in project_data:
        abort(404)
    if view is not None and view not in view_classes:
        abort(404)
    entity = Entity.get_entity_from_oa(id_)
    linked_entities = get_entities_linked_to_entity(id_)
    relations = get_relations(
        get_relation_entities(linked_entities, entity.relations or []))
    related_places = []
    if 'places' in relations:
        related_places = get_related_geoms(relations['places'])
    return render_template(
        'explore/project_entity_view.html',
        entity=entity,
        type_hierarchy=get_types_sorted(entity.types or []),
        images=numpy.array_split(
            entity.depictions, 4)  # type: ignore[arg-type]
        if entity.depictions else None,
        relations=relations,
        related_places=related_places,
        path=(project, view),
        system_classes=system_classes)



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


@app.errorhandler(HTTPException)
def handle_http_exception(
        e: HTTPException) -> (tuple[Response, int | None] |
                              tuple[str, Literal[404, 403, 418] | int]):
    if request.path.startswith('/api/'):
        return jsonify({
            'error': e.description,
            'code': e.code
        }), e.code

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
        'error.html',
        code=code,
        title=title,
        description=description
    ), code


@app.errorhandler(Exception)
def handle_generic_exception(
        e: Exception) -> Response | tuple[str, int] | tuple[Response, int]:
    if isinstance(e, HTTPException):
        return handle_http_exception(e)

    app.logger.error(f"Unhandled exception: {e}", exc_info=True)

    if request.path.startswith('/api/'):
        return jsonify({
            'error': _('Internal Server Error'),
            'code': 500
        }), 500

    return render_template(
        'error.html',
        code=500,
        title=_("Internal Server Error"),
        description=_(
            "An unexpected server error occurred. "
            "Our cartographers are looking into it.")
    ), 500


