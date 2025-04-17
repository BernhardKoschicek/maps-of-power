from flask_babel import lazy_gettext as _

from mop.data.institutes import institutes
from mop.util import get_dates_formatted

results = {
    'text': [],
    'list': [],
    'icons': [{
        'label': _('Final project report'),
        'link': None,
        'file': 'FWF_P 30384-G28_Final_Report.pdf',
        'icon': 'bi bi-journals',
    }]}

images = [
    {
        'src': 'border_all.png',
        'description': _(
            'Interpretation of the Byzantino-Serbian Border between 1228 and '
            '1334 from Different Authors'),
        'citation': 'Bernhard Koschicek, 2018',
        'category': ['borderzones']
    }, {
        'src': 'fortifications.png',
        'description': _(
            'Fortifications in the Northern Macedonian Region in the '
            '13/14th century'),
        'citation': 'Bernhard Koschicek, 2019',
        'category': ['borderzones']
    }, {
        'src': 'Marschroute_Abstract_cyrillic_km.png',
        'description': _('Road Model based on a k. u k. Marching Map'),
        'citation': 'Bernhard Koschicek, 2018',
        'category': ['borderzones']
    }, {
        'src': 'borderzones_markovi_kuli.jpg',
        'description': _(
            'Markovi Kuli Castle near Prilep from the south, Republic '
            'of Northern Macedonia'),
        'citation': 'M. St. Popović, TIB 16, 2007',
        'category': ['borderzones']
    },
    {
        'src': 'borderzones_kale_skopje.jpg',
        'description': _(
            'The Kale elevation in Skopje, Republic of Northern Macedonia'),
        'citation': 'M. St. Popović, TIB 16, 2016',
        'category': ['borderzones']
    },
    {
        'src': 'borderzones_ohrid_stadttor.jpg',
        'description': _(
            'The old city gate of Ohrid, Republic of Northern Macedonia'),
        'citation': 'M. St. Popović, TIB 16, 2018',
        'category': ['borderzones']
    },
    {
        'src': 'borderzones_ohrid_samuilova.jpg',
        'description': _(
            'Ohrid and Samuilova tvrdina Castle, '
            'Republic of Northern Macedonia'),
        'citation': 'M. St. Popović, TIB 16, 2018',
        'category': ['borderzones']
    }, ]

project_borderzones = {
    'acronym': 'borderzones',
    'title': _(
        'Byzantino-Serbian Border Zones in Transition: Migration and Elite '
        'Change in pre-Ottoman Macedonia (1282–1355)'),
    'host_institutes': [institutes['abf']],
    'funded_by': [institutes['fwf']],
    'project_number': 'P 30384-G28',
    'pi': ['Mihailo Popović'],
    'cooperation': '',
    'employees': ['Bernhard Koschiček-Krombholz', 'Vratislav Zervan'],
    'begin': get_dates_formatted(2017, 10, 1),
    'end': get_dates_formatted(2022, 3, 31),
    'description': [
        _('borderzones_description_1'),
        _('borderzones_description_2'),
        _('borderzones_description_3'),
        _('borderzones_description_4')],
    'results': results,
    'icon': 'borderzones_icon.jpg',
    'images': images,
    'videos': [],
    'oaID': '9962',
}
