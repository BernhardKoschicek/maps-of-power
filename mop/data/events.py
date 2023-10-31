from flask_babel import lazy_gettext as _

from mop.data.team import team
from mop.util import get_dates_formatted

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
    'id': 'belgrade_190923',
    'type': types['presentation'],
    'date': f"{get_dates_formatted(2023, 9, 19)}",
    'who': '',
    'icon': 'belgrade_190923.png',
    'title': _('Two Presentations on the Usefulness of OpenAtlas'),
    'description': _('belgrade_190923'),
    'attachment': [{
        'path': '',
        'type': ''}]
},{
    'id': 'athos_oxford_290923',
    'type': types['presentation'],
    'date': f"{get_dates_formatted(2023, 9, 29)}",
    'who': [team['mpopovic']],
    'icon': 'athos_oxford_290923.png',
    'title': _('Workshop on Medieval Athos in Oxford'),
    'description': _('athos_oxford_290923'),
    'attachment': [{
        'path': '',
        'type': ''}]
},{
    'id': 'tripps_070923',
    'type': types['presentation'],
    'date': f"{get_dates_formatted(2023, 9, 7)}",
    'who': '',
    'icon': 'tripps_070923.jpg',
    'title': _('Paper on the Crown of the Saint King Stefan Dečanski'),
    'description': _('tripps_070923'),
    'attachment': [{
        'path': '',
        'type': ''}]
},{
    'id': 'imc_leeds_23',
    'type': types['presentation'],
    'date': f"{get_dates_formatted(2023, 7, 6)}",
    'who': '',
    'icon': 'imc_leeds_23.jpg',
    'title': _('TIB Balkans at the IMC Leeds 2023'),
    'description': _('imc_leeds_23'),
    'attachment': [{
        'path': '',
        'type': ''}]
},{
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
}, {
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
}]
