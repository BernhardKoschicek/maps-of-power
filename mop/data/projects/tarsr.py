from flask_babel import lazy_gettext as _

from mop.data.institutes import institutes
from mop.util import get_dates_formatted


images = [{
    'src': 'tarsr_1.jpg',
    'description':
        _('The Road Tunnel in Honour of the German Emperor Wilhelm '
                     'II from 1916 in the Valley of the River Vardar'),
    'citation': 'M. Popović, 2016',
    'category': ['tarsr']
}, {
    'src': 'tarsr_2.jpg',
    'description':
        _('Inscription in Honour of the German Emperor Wilhelm II '
                     'at the Entrance to the Road Tunnel'),
    'citation': 'M. Popović, 2016',
    'category': ['tarsr']
}, {
    'src': 'tarsr_3.jpg',
    'description':
        _('German Military Cemetery from the First World War near Bitola'),
    'citation': 'M. Popović, 2016',
    'category': ['tarsr']
}, {
    'src': 'tarsr_4.jpg',
    'description': _('War Relics from the First World War in Mariovo'),
    'citation': 'M. Popović, 2016',
    'category': ['tarsr']
},
]

project_tarsr = {
    'acronym': 'tarsr',
    'title': _(
        'Tracing Archaeological Remains and Scholarly Research of the Central '
        'Powers in the Region of Prilep-Bitola during WW I (1915-1918)'),
    'website': '',
    'host_institutes': [institutes['abf'], institutes['ukim']],
    'funded_by': [institutes['oead']],
    'project_number': 'MK 07/2024',
    'pi': [
        f'Mihailo Popović ({_("Vienna")})',
        f'Viktor Lilchikj Adams ({_("Skopje")})'],
    'cooperation': [],
    'employees': [
        f'Toni Filiposki ({_("Skopje")})',
        f'Ordanče Petrov ({_("Prilep")})',
        f'Filip Markovski ({_("Bitola")})',
        f'Hristijan Petrovski ({_("Skopje")})',
        f'Dorota Vargová  ({_("Vienna")})',
        f'Lukas Neugebauer ({_("Vienna")})'],
    'begin': get_dates_formatted(2024, 1, 1),
    'end': get_dates_formatted(2025, 12, 31),
    'description': [
        _('tracing_description_1'),
        _('tracing_description_2'),
        _('tracing_description_3'),
        _('tracing_description_4'),
        _('tracing_description_5'),
    ],
    'results': '',
    'icon': '',
    'images': images,
    'videos': [],
    'oaID': '135005',
}
