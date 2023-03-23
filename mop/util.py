from datetime import datetime
from typing import Any

from flask import url_for
from flask_babel import lazy_gettext as _

from mop import app


def get_dates_formatted(year: int, month: int, day: int) -> str:
    return datetime(year, month, day).strftime('%d.%m.%Y')


@app.context_processor
def inject_menu() -> dict[str, Any]:
    content = ['about', 'projects', 'software', 'events', 'histgeo']
    navbar = [
        {'name': _('about'), 'to': url_for('about')},
        {'name': _('projects'), 'to': url_for('projects')},
        {'name': _('software'), 'to': url_for('software')},
        {'name': _('events'), 'to': url_for('events')}]

    return dict(
        content=content,
        navbar=navbar)
