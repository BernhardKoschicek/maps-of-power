from flask import url_for

from mop import app


@app.template_filter()
def display_menu(route: str) -> str:
    html = ''
    for item in ['about', 'projects', 'cooperation', 'software', 'events']:
        active = 'active' if route.startswith('/' + item) \
                             or item == 'about' and route in ['/'] else ''
        html += \
            f'<li class="nav-item">' \
            f'<a class="nav-link {active}" href="{url_for(item)}">' \
            f'{item.upper()}</a></li>'
    return html

