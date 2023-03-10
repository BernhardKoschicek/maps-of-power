from typing import Optional

from flask import render_template, session, request
from werkzeug import Response
from werkzeug.utils import redirect

from display.events import display_event  # pylint: disable=import-error
from mop.data.images import category_images
from mop.data.events import event_list
from mop.display.image import image_gallery
from mop import app


@app.route('/')
def about() -> str:
    return render_template(
        'about.html',
        category_images=image_gallery(category_images),
        events=display_event(event_list))


@app.route('/projects')
def projects() -> str:
    return render_template('layout.html')


@app.route('/software')
def software() -> str:
    return render_template('layout.html')


@app.route('/events')
def events() -> str:
    return render_template('layout.html')


@app.route('/language=<language>')
def set_language(language: Optional[str] = None) -> Response:
    session['language'] = language
    return redirect(request.referrer)
