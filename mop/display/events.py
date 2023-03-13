from typing import Any

from markupsafe import Markup


def display_event(events: list[dict[str, Any]]) -> str:
    html = ''
    for event in events:
        html += f'''
            <div class="col-sm-4 col-md-3 py-3">
              <div class="card border-primary">
              <img src="{event['icon']}" 
                  class="card-img-top" 
                  alt="{event['id']}Image">
                <div class="card-body">
                  <h3 class="card-title">{event['title']}</h3>
                  <p class="card-text">{event['description']}</p>
                </div>
              </div>
            </div>
            '''
    return Markup(html)
