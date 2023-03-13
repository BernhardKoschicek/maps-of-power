from pathlib import Path
from typing import Any

from flask import Flask, Response, session, request
from flask_babel import Babel
import sass
from wand.image import Image

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

sass.compile(
    dirname=(STATIC_PATH / 'scss', STATIC_PATH / 'css'),
    output_style='compressed')


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


# Make only if thumbnail not exist for production
@app.before_first_request
def create_thumbnails():
    for file in IMAGE_PATH.rglob("*"):
        if file.is_file() and file.suffix.lower() in ['.jpg', '.png', '.jpeg']:
            with Image(filename=file) as src:
                src.resize(400, 400)
                src.save(
                    filename=THUMBNAIL_PATH / file.name)


@app.after_request
def apply_caching(response: Response) -> Response:
    response.headers['Strict-Transport-Security'] = \
        'max-age=31536000; includeSubDomains'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response
