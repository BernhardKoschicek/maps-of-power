from collections import defaultdict
from typing import Optional

import numpy
from flask import render_template, session, request
from werkzeug import Response
from werkzeug.utils import redirect

from mop.model.api_calls import get_entities_linked_to_entity
from mop.model.entity import Entity
from mop.model.explore import view_classes, get_oa_by_view_class, system_classes
from mop import app
from mop.data.events import event_list
from mop.data.histgeo import newsletters, volumes, lectures
from mop.data.images import category_images
from mop.data.literature import literatures
from mop.data.presentations import presentations
from mop.data.projects.projects import project_data
from mop.display.image import image_gallery
from mop.util import get_dict_entries_by_category, get_relations, \
    get_relation_entities, get_related_geoms, get_types_sorted


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
    data = False
    try:
        data = get_oa_by_view_class(view, project_data[project]['oaID'])
    except:
        pass
    return render_template(
        'explore/project_explore_table.html',
        data=data,
        project=project_data[project],
        view_classes=view_classes[view],
        view=view)


@app.route('/projects')
@app.route('/projects/<project>/explore/<view>/<id_>')
def entity_project_view(
        id_: int,
        project: Optional[str],
        view: Optional[str]) -> str:
    entity = Entity.get_entity_from_oa(id_)
    linked_entities = get_entities_linked_to_entity(id_)
    relations = get_relations(
        get_relation_entities(linked_entities, entity.relations))
    related_places = get_related_geoms(relations['places']) \
        if 'places' in relations else []
    return render_template(
        'explore/project_entity_view.html',
        entity=entity,
        type_hierarchy=get_types_sorted(entity.types),
        images=numpy.array_split(entity.depictions, 4)
        if entity.depictions else None,
        relations=relations,
        related_places=related_places,
        path=(project, view),
        system_classes=system_classes)


@app.route('/software')
def software() -> str:
    return render_template('software.html')


@app.route('/atlas')
@app.route('/frontend')
def frontend() -> str:
    return redirect("https://map.geo.univie.ac.at/projects/mop/")
