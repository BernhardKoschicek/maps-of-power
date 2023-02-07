from pathlib import Path
from flask import Flask, Response, session, request
from flask_babel import Babel

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config')
babel = Babel(app)

if (Path(app.root_path).parent / 'instance' / 'production.py').is_file():
    app.config.from_pyfile('production.py')

# pylint: disable=wrong-import-position, import-outside-toplevel
from mop import views


@babel.localeselector
def get_locale() -> str:
    return session.get(
        'language',
        request.accept_languages.best_match(app.config['LANGUAGES'].keys()))


@app.context_processor
def inject_conf_var():
    return dict(
        AVAILABLE_LANGUAGES=app.config['LANGUAGES'],
        CURRENT_LANGUAGE=session.get(
            'language',
            request.accept_languages.best_match(
                app.config['LANGUAGES'].keys())))


@app.after_request
def apply_caching(response: Response) -> Response:
    response.headers['Strict-Transport-Security'] = \
        'max-age=31536000; includeSubDomains'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response
