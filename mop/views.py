from collections import defaultdict
from typing import Optional

from flask import render_template, session, request
from werkzeug import Response
from werkzeug.utils import redirect

from data.explore import view_classes
from mop import app
from mop.data.events import event_list
from mop.data.histgeo import newsletters, volumes, lectures
from mop.data.images import category_images
from mop.data.literature import literatures
from mop.data.presentations import presentations
from mop.data.projects.projects import project_data
from mop.display.image import image_gallery
from mop.util import get_dict_entries_by_category


@app.route('/')
def about() -> str:
    return render_template(
        'about.html',
        category_images=image_gallery(category_images),
        events=event_list)


@app.route('/events')
def events() -> str:
    return render_template('events.html', events=event_list)


@app.route('/explore')
def explore() -> str:
    return render_template(
        'explore.html',
        subprojects_dict=project_data,
        view_classes=view_classes)


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


@app.route('/software')
def software() -> str:
    return render_template('software.html')
