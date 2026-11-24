import os
from pathlib import Path
from typing import TYPE_CHECKING, Any

from flask import Flask, Response, current_app, request, session, url_for
from werkzeug.middleware.proxy_fix import ProxyFix

from mop.extensions import babel, cache, set_default_app
from mop.pid import pid_bp
from mop.tib_views import tib_bp
from mop.util import inject_menu
from mop.views import explore_bp, main_bp

ROOT_PATH = Path(__file__).parent
BASE_PATH = ROOT_PATH.parent
STORAGE_PATH = BASE_PATH / 'storage'
DATA_PATH = STORAGE_PATH / 'data'
MEDIA_PATH = STORAGE_PATH / 'media'
STATIC_PATH = ROOT_PATH / 'static'
IMAGE_PATH = MEDIA_PATH / 'images'
THUMBNAIL_PATH = MEDIA_PATH / 'thumbnails'


def _compute_assets_version() -> int:
    env_ver = os.environ.get('ASSETS_VERSION', '').strip()
    if env_ver.isdigit():
        return int(env_ver)
    try:
        return int((BASE_PATH / 'pyproject.toml').stat().st_mtime)
    except OSError:  # pragma: no cover
        return 1


ASSETS_VERSION = _compute_assets_version()


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

    if application.config.get('USE_PROXY_FIX'):
        setattr(
            application,
            'wsgi_app',
            ProxyFix(
                application.wsgi_app, x_for=1, x_proto=1, x_host=1))

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
        response.headers['X-XSS-Protection'] = '0'
        response.headers['Referrer-Policy'] = (
            'strict-origin-when-cross-origin')
        response.headers['Permissions-Policy'] = (
            'geolocation=(), microphone=(), camera=()')
        response.headers['Content-Security-Policy'] = (
            "base-uri 'self'; frame-ancestors 'self'; object-src 'none'")
        return response

    return application


if TYPE_CHECKING:
    app: Flask

# pylint: disable=invalid-name
_lazy_app: Flask | None = None


def __getattr__(name: str) -> Any:
    # pylint: disable=global-statement
    global _lazy_app
    if name == 'app':
        if _lazy_app is None:
            _lazy_app = create_app()
        return _lazy_app
    raise AttributeError(
        f"module {__name__!r} has no attribute {name!r}")


# pylint: disable=undefined-all-variable
__all__ = [
    'ASSETS_VERSION',
    'BASE_PATH',
    'DATA_PATH',
    'IMAGE_PATH',
    'MEDIA_PATH',
    'ROOT_PATH',
    'STATIC_PATH',
    'STORAGE_PATH',
    'THUMBNAIL_PATH',
    'app',
    'babel',
    'cache',
    'create_app',
    'get_locale',
]
