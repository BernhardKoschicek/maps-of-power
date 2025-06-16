from flask_babel import lazy_gettext as _

from mop.data.institutes import institutes
from mop.util import get_dates_formatted


images = [{
    'src': 'dgse_1.jpg',
    'description':
        _('The Parish Church of Saint Andrew in Ebreichsdorf from the South-East'),
    'citation': 'Elisabeth Humer-Popović',
    'category': ['dgse']
}, {
    'src': 'dgse_2.jpg',
    'description': _('The Luckate Stein'),
    'citation': 'Elisabeth Humer-Popović',
    'category': ['dgse']
},
    {
    'src': 'dgse_3.jpg',
    'description':
        _('View of the Area around the Castle of Ebreichsdorf from the East'),
    'citation': 'M. Popović',
    'category': ['dgse']
},
    {
    'src': 'dgse_4.jpg',
    'description': _('The Castle of Pottendorf'),
    'citation': 'Wikipedia (https://de.wikipedia.org/wiki/Schloss_Pottendorf#/media/Datei:Pottendorf_-_Schloss,_S%C3%BCdansicht2.JPG)',
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
       'Marija Đokić Petrović',
       'Silvia Gómez-Senovilla',
        'Veronika Kochesser-Latzer'
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
