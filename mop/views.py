from typing import Optional

from flask import render_template, session, request
from werkzeug import Response
from werkzeug.utils import redirect

from mop import app


@app.route('/')
def home() -> str:
    return render_template('layout.html')


@app.route('/language=<language>')
def set_language(language: Optional[str] = None) -> Response:
    session['language'] = language
    return redirect(request.referrer)
