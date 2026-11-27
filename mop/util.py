from datetime import datetime
from typing import Any, Union, Optional

from flask import url_for
from flask_babel import lazy_gettext as _
from markupsafe import Markup, escape

from mop.model.types import Types
from mop.model.util import sanitize_external_url


def get_dates_formatted(year: int, month: int, day: int) -> str:
    return datetime(year, month, day).strftime('%d.%m.%Y')


def get_table_dates_formatted(year: int, month: int, day: int) -> str:
    return datetime(year, month, day).strftime('%Y/%m/%d')


def _sanitize_asset_src(src: str | None) -> str:
    if not src:
        return ''
    cleaned = src.strip()
    if (cleaned.startswith('/')
            and not cleaned.startswith('//')
            and '\\' not in cleaned):
        return cleaned
    return sanitize_external_url(cleaned)


def youtube_iframe(
        link_: str,
        left_logo: Optional[str] = None,
        right_logo: Optional[str] = None) -> Markup:
    safe_link = escape(sanitize_external_url(link_))
    safe_left = escape(_sanitize_asset_src(left_logo)) if left_logo else ''
    safe_right = (
        escape(_sanitize_asset_src(right_logo)) if right_logo else '')

    if not safe_left and not safe_right:
        return Markup(  # nosec B704
            '<div class="col-12 col-md-8 text-center">'
            '<div class="ratio ratio-16x9 rounded-4 '
            'overflow-hidden border shadow-sm">'
            f'<iframe width="560" height="315" src="{safe_link}" '
            'title="YouTube video player" '
            'allow="accelerometer; autoplay; clipboard-write; '
            'encrypted-media; gyroscope; picture-in-picture" '
            'allowfullscreen></iframe>'
            '</div>'
            '</div>')

    left_col = (
        '<div class="col-6 col-md-2 order-2 order-md-1 '
        'd-flex align-items-center justify-content-center p-2">'
        f'<img src="{safe_left}" class="img-fluid video-image-size" alt="">'
        '</div>'
    ) if safe_left else '<div class="col-md-2 d-none d-md-block"></div>'

    video_col = (
        '<div class="col-12 col-md-8 order-1 order-md-2 text-center">'
        '<div class="ratio ratio-16x9 rounded-4 '
        'overflow-hidden border shadow-sm">'
        f'<iframe width="560" height="315" src="{safe_link}" '
        'title="YouTube video player" '
        'allow="accelerometer; autoplay; clipboard-write; '
        'encrypted-media; gyroscope; picture-in-picture" '
        'allowfullscreen></iframe>'
        '</div>'
        '</div>'
    )

    right_col = (
        '<div class="col-6 col-md-2 order-3 order-md-3 '
        'd-flex align-items-center justify-content-center p-2">'
        f'<img src="{safe_right}" class="img-fluid video-image-size" alt="">'
        '</div>'
    ) if safe_right else '<div class="col-md-2 d-none d-md-block"></div>'

    return Markup(f'{left_col}\n{video_col}\n{right_col}')  # nosec B704


def youtube_iframe_with_logos(
        link_: str,
        left_logo: Optional[str] = None,
        right_logo: Optional[str] = None) -> Markup:
    return youtube_iframe(link_, left_logo=left_logo, right_logo=right_logo)


def get_image_frame(filepath: str) -> Markup:
    safe_path = escape(_sanitize_asset_src(filepath))
    return Markup(  # nosec B704
        f'<img src="{safe_path}" '
        'class="img-fluid video-image-size" alt="">')


def inject_menu() -> dict[str, Any]:
    navbar = [{
        'name': _('about'),
        'to': url_for('main.about')}, {
        'name': _('projects'),
        'to': url_for('explore.projects')}, {
        'name': _('atlas'),
        'to': url_for('main.frontend')}, {
        'name': 'histgeo',
        'to': url_for('main.histgeo')}, {
        'name': _('events'),
        'to': url_for('main.events')}, {
        'name': _('literature'),
        'to': url_for('main.literature')}, {
        'name': 'TIB',
        'to': url_for('tib.tib_overview')}]
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


def array_split(lst: list[Any], num_chunks: int) -> list[list[Any]]:
    """Split a list into num_chunks nearly equal sublists."""
    k, m = divmod(len(lst), num_chunks)
    return [
        lst[i * k + min(i, m):(i + 1) * k + min(i + 1, m)]
        for i in range(num_chunks)]
