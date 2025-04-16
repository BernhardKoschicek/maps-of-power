from flask_babel import lazy_gettext as _

from mop.data.institutes import institutes
from mop.util import get_dates_formatted

images = [{
    'src': 'tib_balkan_1.jpg',
    'description': _('The Monastery of Saint Naum on Lake Ohrid'),
    'citation': 'Johannes Koder, 1965',
    'category': ['tib_balkan']
}, {
    'src': 'tib_balkan_2.jpg',
    'description': _('The Monastery of Saint Naum on Lake Ohrid'),
    'citation': 'Mihailo Popović, 2017',
    'category': ['tib_balkan']
}, {
    'src': 'tib_balkan_3.jpg',
    'description': _('The Church of Sveti Jovan Kaneo in Ohrid'),
    'citation': 'Wolfgang Lanz, 1970',
    'category': ['tib_balkan']
}, {
    'src': 'tib_balkan_4.jpg',
    'description': _('The Church of Sveti Jovan Kaneo in Ohrid'),
    'citation': 'Mihailo Popović, 2008',
    'category': ['tib_balkan']
}]

project_tib_balkan = {
    'acronym': 'tib_balkan',
    'title': _(
        'Reverse Engineering of the Tabula Imperii Byzantini Balkans'),
    'website':
        'https://tib.oeaw.ac.at/',
    'host_institutes': [institutes['abf']],
    'funded_by': [],
    'project_number': '',
    'pi': ['Mihailo Popović'],
    'cooperation': [],
    'employees': [],
    'begin': get_dates_formatted(2025, 1, 1),
    'end': 'Ongoing',
    'description': [
        _('tib_balkan_description_1'),
        _('tib_balkan_description_2'),
        _('tib_balkan_description_3'),
    ],
    'results': '',
    'icon': '',
    'images': images,
    'videos': '',
    'oaID': '124483',
}
