from datetime import datetime
from typing import Any, Union, Optional

from flask import url_for
from flask_babel import lazy_gettext as _

from mop.model.types import Types
from mop import app


def get_dates_formatted(year: int, month: int, day: int) -> str:
    return datetime(year, month, day).strftime('%d.%m.%Y')


def get_table_dates_formatted(year: int, month: int, day: int) -> str:
    return datetime(year, month, day).strftime('%Y/%m/%d')


def youtube_iframe(
        link_: str,
        left_logo: Optional[str] = None,
        right_logo: Optional[str] = None) -> str:
    if not left_logo and not right_logo:
        return '<div class="col-12 col-md-8 text-center">' \
               '<div class="ratio ratio-16x9 rounded-4 overflow-hidden border shadow-sm">' \
               f'<iframe width="560" height="315" src="{link_}" ' \
               'title="YouTube video player" ' \
               'allow="accelerometer; autoplay; clipboard-write; ' \
               'encrypted-media; gyroscope; picture-in-picture" ' \
               'allowfullscreen></iframe>' \
               '</div>' \
               '</div>'

    left_col = (
        '<div class="col-6 col-md-2 order-2 order-md-1 d-flex align-items-center justify-content-center p-2">'
        f'<img src="{left_logo}" class="img-fluid video-image-size" alt="">'
        '</div>'
    ) if left_logo else '<div class="col-md-2 d-none d-md-block"></div>'

    video_col = (
        '<div class="col-12 col-md-8 order-1 order-md-2 text-center">'
        '<div class="ratio ratio-16x9 rounded-4 overflow-hidden border shadow-sm">'
        f'<iframe width="560" height="315" src="{link_}" '
        'title="YouTube video player" '
        'allow="accelerometer; autoplay; clipboard-write; '
        'encrypted-media; gyroscope; picture-in-picture" '
        'allowfullscreen></iframe>'
        '</div>'
        '</div>'
    )

    right_col = (
        '<div class="col-6 col-md-2 order-3 order-md-3 d-flex align-items-center justify-content-center p-2">'
        f'<img src="{right_logo}" class="img-fluid video-image-size" alt="">'
        '</div>'
    ) if right_logo else '<div class="col-md-2 d-none d-md-block"></div>'

    return f'{left_col}\n{video_col}\n{right_col}'


def youtube_iframe_with_logos(
        link_: str,
        left_logo: Optional[str] = None,
        right_logo: Optional[str] = None) -> str:
    return youtube_iframe(link_, left_logo=left_logo, right_logo=right_logo)


def get_image_frame(filepath: str) -> str:
    return f'<img src="{filepath}" ' \
           'class="img-fluid video-image-size" alt="">'


@app.context_processor
def inject_menu() -> dict[str, Any]:
    navbar = [{
        'name': _('about'),
        'to': url_for('about')}, {
        'name': _('projects'),
        'to': url_for('projects')}, {
        'name': _('atlas'),
        'to': url_for('frontend')}, {
        'name': 'histgeo',
        'to': url_for('histgeo')}, {
        'name': _('events'),
        'to': url_for('events')}, {
        'name': _('literature'),
        'to': url_for('literature')}]
    return {'navbar': navbar}


def get_dict_entries_by_category(
        categories: Union[list[str], str],
        list_: list[dict[str, Any]]) -> list[dict[str, Any]]:
    categories = [categories] if isinstance(categories, str) else categories
    return [
        entry for entry in list_ if any(
            item in categories for item in entry['category'])]


def get_types_sorted(types: list[Types]) -> Optional[dict[str, Any]]:
    if not types:
        return None
    type_hierarchy: dict[str, Any] = {}
    for type_ in types:
        type_hierarchy.setdefault(type_.root, []).append(type_)
    return type_hierarchy
