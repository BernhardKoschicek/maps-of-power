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
    'id': 'presse_03052025',
    'type': types['presentation'],
    'date': f"{get_dates_formatted(2025, 5, 3)}",
    'who': '',
    'icon': 'presse_03052025.jpg',
    'title': _('Report in the Newspaper Die Presse'),
    'description': _('presse_03052025'),
    'attachment': [{
        'path': '',
        'type': ''}]
},{
    'id': 'wittgenstein_13022025',
    'type': types['presentation'],
    'date': f"{get_dates_formatted(2025, 2, 13)}",
    'who': '',
    'icon': 'wittgenstein_13022025.jpg',
    'title': _('Lecture at the Haus Wittgenstein'),
    'description': _('wittgenstein_13022025'),
    'attachment': [{
        'path': '',
        'type': ''}]
},{
    'id': 'workshop_oxford_300524',
    'type': types['science_fair'],
    'date': f"{get_dates_formatted(2024, 5, 30)}",
    'who': '',
    'icon': 'workshop_oxford_300524.jpg',
    'title': _('Workshop in Oxford'),
    'description': _('workshop_oxford_300524'),
    'attachment': [{
        'path': '',
        'type': ''}]
},{
    'id': 'lange_nacht_der_forschung_240524',
    'type': types['presentation'],
    'date': f"{get_dates_formatted(2024, 5, 24)}",
    'who': '',
    'icon': 'lange_nacht_der_forschung_240524.jpg',
    'title': _('The Long Night of Research in Vienna'),
    'description': _('lange_nacht_der_forschung_240524'),
    'attachment': [{
        'path': '',
        'type': ''}]
},{
    'id': 'koder_festschrift_230424',
    'type': types['book_release'],
    'date': f"{get_dates_formatted(2024, 4, 23)}",
    'who': '',
    'icon': 'koder_festschrift_230424.jpg',
    'title': _('Presentation of an Edited Volume in Honor of Johannes Koder'),
    'description': _('koder_festschrift_230424'),
    'attachment': [{
        'path': '',
        'type': ''}]
},{
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
