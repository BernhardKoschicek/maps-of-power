from mop.data.team import team
from mop.util import get_dates_formatted
from flask_babel import lazy_gettext as _

types = {
    'presentation': {
        'name': _('presentation'),
        'bs_icon': 'bi-chat-text-fill'
    },
    'online_presentation': {
        'name': _('presentation'),
        'bs_icon': 'bi-chat-right-text-fill'
    },
    'award': {
        'name': _('award'),
        'bs_icon': 'bi-award'
    },
    'science_fair': {
        'name': _('science_fair'),
        'bs_icon': 'bi-mortarboard-fill'
    },
    'book_release': {
        'name': _('book_release'),
        'bs_icon': 'bi-book'
    },
    'blog_post': {
        'name': _('blogpost'),
        'bs_icon': 'bi-blockquote-right'
    },
}
event_list = [{
    'id': 'mecern_2023',
    'type': types['presentation'],
    'date': f"{get_dates_formatted(2023, 4, 27)}",
    'who': [team['mpopovic']],
    'icon': 'mecern_2023.jpg',
    'title': _('presentation on MECERN conference'),
    'description': _('mecern_2023'),
    'attachment': [{
        'path': '',
        'type': ''}]
},{
    'id': 'serbian_academy_220223',
    'type': types['presentation'],
    'date': f"{get_dates_formatted(2023, 2, 22)}",
    'who': [team['mpopovic']],
    'icon': 'serbian_academy_220223.jpg',
    'title': _('presentation at the Serbian Academy of Sciences and Arts'),
    'description': _('serbian_academy_220223'),
    'attachment': [{
        'path': '',
        'type': ''}]
},
]
