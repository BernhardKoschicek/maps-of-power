from flask import render_template, session, request
from werkzeug.utils import redirect

from mop import app


@app.route('/')
def tib_home() -> str:
    return render_template('layout.html')


@app.route('/language=<language>')
def set_language(language=None):
    session['language'] = language
    return redirect(request.referrer)
