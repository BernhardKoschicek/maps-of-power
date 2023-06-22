from datetime import datetime
from typing import Any, Union

from flask import url_for
from flask_babel import lazy_gettext as _

from mop import app


def get_dates_formatted(year: int, month: int, day: int) -> str:
    return datetime(year, month, day).strftime('%d.%m.%Y')


def get_table_dates_formatted(year: int, month: int, day: int) -> str:
    return datetime(year, month, day).strftime('%Y/%m/%d')


def youtube_iframe(link_: str) -> str:
    return '<iframe width="560" height="315" ' \
           f'src="{link_}" ' \
           'title="YouTube video  player" ' \
           'allow="accelerometer; autoplay; clipboard-write;  ' \
           'encrypted-media; gyroscope; picture-in-picture" ' \
           'allowfullscreen></iframe>'


@app.context_processor
def inject_menu() -> dict[str, Any]:
    content = ['about', 'projects', 'software', 'events', 'histgeo']
    navbar = [
        {'name': _('about'), 'to': url_for('about')},
        {'name': _('projects'), 'to': url_for('projects')},
        {'name': _('software'), 'to': url_for('software')},
        {'name': 'histgeo', 'to': url_for('histgeo')},
        {'name': _('events'), 'to': url_for('events')},
        {'name': _('literature'), 'to': url_for('literature')}]

    return dict(
        content=content,
        navbar=navbar)


def get_dict_entries_by_category(
        categories: Union[list[str], str],
        list_: list[dict[str, Any]]) -> list[dict[str, str]]:
    categories = [categories] if type(categories) == str else categories
    return [entry for entry in list_
            if any(item in categories for item in entry['category'])]
