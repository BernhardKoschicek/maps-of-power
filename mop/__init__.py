import os
from pathlib import Path
import time
from typing import Any

from flask import Flask, Response, current_app, request, session, url_for

from mop.extensions import babel, cache, set_default_app
from mop.pid import pid_bp
from mop.tib_views import tib_bp
from mop.util import inject_menu
from mop.views import explore_bp, main_bp

ROOT_PATH = Path(__file__).parent
STATIC_PATH = ROOT_PATH / 'static'
IMAGE_PATH = STATIC_PATH / 'images'
THUMBNAIL_PATH = STATIC_PATH / 'thumbnails'

ASSETS_VERSION = int(time.time())


def get_locale() -> str:
    lang = session.get('language')
    if lang:
        return str(lang)
    try:
        return (
            request.accept_languages.best_match(
                current_app.config['LANGUAGES'])
            or 'en')
    except (RuntimeError, KeyError):
        return 'en'


def create_app(config: dict[str, Any] | None = None) -> Flask:
    application = Flask(__name__, instance_relative_config=True)
    application.config.from_object('config')
    try:
        application.config.from_pyfile('production.py')
    except (FileNotFoundError, OSError):
        pass

    if config:
        application.config.update(config)

    set_default_app(application)

    # Initialize extensions
    babel.init_app(application, locale_selector=get_locale)
    cache.init_app(application)

    # Register blueprints (pid_bp last as catch-all)
    application.register_blueprint(main_bp)
    application.register_blueprint(explore_bp)
    application.register_blueprint(tib_bp)
    application.register_blueprint(pid_bp)

    # Handle unprefixed url_for calls in templates
    def _handle_url_build_error(
            error: Exception, endpoint: str,
            values: dict[str, Any]) -> str:
        for bp_name in ('main', 'explore', 'tib', 'pid'):
            candidate = f"{bp_name}.{endpoint}"
            if candidate in application.view_functions:
                return url_for(candidate, **values)
        raise error

    application.url_build_error_handlers.append(_handle_url_build_error)

    @application.before_request
    def before_request() -> None:
        proxy = application.config.get('API_PROXY')
        if proxy:
            os.environ['http_proxy'] = proxy
            os.environ['https_proxy'] = proxy

    @application.context_processor
    def inject_conf_var() -> dict[str, Any]:
        return {
            'AVAILABLE_LANGUAGES': application.config.get('LANGUAGES', []),
            'CURRENT_LANGUAGE': get_locale(),
            'ASSETS_VERSION': ASSETS_VERSION}

    application.context_processor(inject_menu)

    @application.after_request
    def apply_caching(response: Response) -> Response:
        response.headers['Strict-Transport-Security'] = (
            'max-age=31536000; includeSubDomains')
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        return response

    return application


app = create_app()

__all__ = [
    'ASSETS_VERSION',
    'IMAGE_PATH',
    'ROOT_PATH',
    'STATIC_PATH',
    'THUMBNAIL_PATH',
    'app',
    'babel',
    'cache',
    'create_app',
    'get_locale',
]
