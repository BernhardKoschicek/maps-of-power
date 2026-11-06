from typing import Any

from flask import url_for
from markupsafe import Markup, escape


def image_gallery(images: dict[str, Any]) -> str:
    html = ''
    for key, value in images.items():
        escaped_key = escape(key)
        escaped_src = escape(value["src"])
        escaped_caption = escape(value["caption"])
        escaped_citation = escape(value["citation"])
        escaped_desc = escape(value.get("description", ""))

        img_url = url_for('main.serve_media', filename=f'images/{escaped_src}')
        thumb_url = url_for(
            'main.serve_media', filename=f'thumbnails/{escaped_src}')
        html += '<div class="col-lg-3"><figure class="figure">'
        html += (
            f'<a href="{img_url}"'
            f' data-caption="{escaped_caption}, {escaped_citation}">'
            f'<img src="{thumb_url}"'
            f' alt="{escaped_key}" class="img-fluid p-4"></a>')
        if escaped_desc:
            html += f'<p>{escaped_desc}</p>'
        html += '</figure></div>'
    return Markup(html)  # nosec B704
