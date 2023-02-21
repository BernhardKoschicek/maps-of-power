from typing import Optional

from flask import render_template, session, request
from werkzeug import Response
from werkzeug.utils import redirect

from data.images import category_images
from mop import app


@app.route('/')
def about() -> str:
    return render_template('about.html', category_images=category_images)


@app.route('/projects')
def projects() -> str:
    return render_template('layout.html')


@app.route('/cooperation')
def cooperation() -> str:
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
