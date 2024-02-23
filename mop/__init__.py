import os
from pathlib import Path
from typing import Any

from flask import Flask, Response, session, request
from flask_babel import Babel


app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config')
app.config.from_pyfile('production.py')
babel = Babel(app)

# pylint: disable=wrong-import-position, import-outside-toplevel
from mop import util, views, data, display

ROOT_PATH = Path(__file__).parent

STATIC_PATH = ROOT_PATH / 'static'
IMAGE_PATH = STATIC_PATH / 'images'
THUMBNAIL_PATH = STATIC_PATH / 'thumbnails'


@app.before_request
def before_request() -> None:
    os.environ['http_proxy'] = app.config['API_PROXY']
    os.environ['https_proxy'] = app.config['API_PROXY']


@babel.localeselector
def get_locale() -> str:
    return session.get(
        'language',
        request.accept_languages.best_match(app.config['LANGUAGES'].keys()))


@app.context_processor
def inject_conf_var() -> dict[str, Any]:
    return {
        'AVAILABLE_LANGUAGES': app.config['LANGUAGES'],
        'CURRENT_LANGUAGE': session.get(
            'language',
            request.accept_languages.best_match(
                app.config['LANGUAGES'].keys()))}


@app.after_request
def apply_caching(response: Response) -> Response:
    response.headers['Strict-Transport-Security'] = \
        'max-age=31536000; includeSubDomains'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response
