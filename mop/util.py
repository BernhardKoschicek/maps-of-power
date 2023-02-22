from flask import url_for
from flask_babel import lazy_gettext as _
from mop import app


@app.template_filter()
def display_menu(route: str) -> str:
    html = ''
    for item in ['about', 'projects', 'cooperation', 'software', 'events']:
        active = 'fw-bold' if route.startswith('/' + item) \
                              or item == 'about' and route in ['/'] else ''
        html += \
            f'<li class="nav-item">' \
            f'<a class="nav-link {active} ' \
            f'text-secondary" href="{url_for(item)}">' + \
            _(item).upper() + '</a></li>'
    return html
