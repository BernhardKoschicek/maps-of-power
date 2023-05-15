from typing import Any

from flask import url_for
from markupsafe import Markup


def image_gallery(images: dict[str, Any]) -> str:
    html = ''
    for key, value in images.items():
        html += '<div class="col-lg-3"><figure class="figure">'
        html += \
            f'<a href="' \
            f'{url_for("static", filename="images/" + value["src"])}"' \
            f' data-caption="{value["caption"]}, {value["citation"]}">' \
            f'<img src="' \
            f'{url_for("static", filename="thumbnails/" + value["src"])}"' \
            f' alt="{key}" class="img-fluid p-4"></a>'
        if value["description"]:
            html += f'<p>{value["description"]}</p>'
        html += '</figure></div>'
    return Markup(html)
