from flask_babel import lazy_gettext as _

from mop.data.institutes import institutes
from mop.util import get_dates_formatted


images = [{
    'src': 'dgse_1.jpg',
    'description':
        _('The (Moated) Castle of Ebreichsdorf'),
    'citation': '',
    'category': ['dgse']
}, {
    'src': 'dgse_2.jpg',
    'description':
        _('Ebreichsdorf in the Survey conducted under Emperor Joseph II (https://www.arcanum.com/en/)'),
    'citation': '',
    'category': ['dgse']
}, {
    'src': 'dgse_3.jpg',
    'description':
        _('View of the Area around the Castle of Ebreichsdorf from the East'),
    'citation': '',
    'category': ['dgse']
}]

project_dgse = {
    'acronym': 'dgse',
    'title': _(
        'Digital Humanities using the Example of the Castle of Ebreichsdorf '
        'in the Lower Austrian Industrial District'),
    'website': '',
    'host_institutes': [institutes['iti']],
    'funded_by': [institutes['noe']],
    'project_number': '',
    'pi': [
        'Bernhard Dolna (ITI)',
        'Richard Drasche-Wartinberg (Schloß Ebreichsdorf)',
        'Mihailo Popović',
    ],
    'cooperation': [],
    'employees': [
       'Nikola Arnautović',
       'Marija Djokić Petrović',
       'Silvia Gómez-Senovilla',
    ],
    'begin': get_dates_formatted(2025, 1, 1),
    'end': get_dates_formatted(2026, 12, 31),
    'description': [
        _('dgse_description_1'),
        _('dgse_description_2'),
        _('dgse_description_3')
    ],
    'results': '',
    'icon': '',
    'images': images,
    'videos': [],
    'oaID': '135379',
}
