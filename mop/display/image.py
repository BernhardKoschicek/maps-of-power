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
        escaped_desc = escape(value["description"]) if value["description"] else ''

        html += '<div class="col-lg-3"><figure class="figure">'
        html += (
            f'<a href="{url_for("static", filename="images/" + escaped_src)}"'
            f' data-caption="{escaped_caption}, {escaped_citation}">'
            f'<img src="{url_for("static", filename="thumbnails/" + escaped_src)}"'
            f' alt="{escaped_key}" class="img-fluid p-4"></a>'
        )
        if escaped_desc:
            html += f'<p>{escaped_desc}</p>'
        html += '</figure></div>'
    return Markup(html)  # nosec B704
