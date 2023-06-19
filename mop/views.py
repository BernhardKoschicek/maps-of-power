from typing import Optional

from flask import render_template, session, request
from werkzeug import Response
from werkzeug.utils import redirect

from data.projects.projects import project_data
from mop import app
from mop.data.events import event_list
from mop.data.histgeo import newsletters, volumes, lectures
from mop.data.images import category_images
from mop.display.image import image_gallery


@app.route('/')
def about() -> str:
    return render_template(
        'about.html',
        category_images=image_gallery(category_images),
        events=event_list)


@app.route('/projects')
@app.route('/projects/<title>')
def projects(title: Optional[str] = None) -> str:
    if title:
        return render_template(
            'project_details.html',
            project=project_data[title])
    return render_template('projects.html', projects=project_data)


@app.route('/software')
def software() -> str:
    return render_template('software.html')


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


@app.route('/events')
def events() -> str:
    return render_template('events.html', events=event_list)


@app.route('/literature')
def literature() -> str:
    return render_template('literature.html', events=event_list)


@app.route('/language=<language>')
def set_language(language: Optional[str] = None) -> Response:
    session['language'] = language
    return redirect(request.referrer)
