from flask_babel import lazy_gettext as _

from mop.data.institutes import institutes
from mop.util import get_dates_formatted

results = {
    'text': [],
    'list': [],
    'icons': [{
        'label': _('Final project report'),
        'link': None,
        'file': 'Project_Report_MK_03_2016.pdf',
        'icon': 'bi bi-journals',
    }]}

images = [
    {
        'src': 'vlachs_1.png',
        'description': _('A Sheepflock in the Village of Oxynon, Greece.'),
        'citation': 'M. Popović, 2004',
        'category': ['vlachs']
    },
    {
        'src': 'vlachs_2.png',
        'description': _('A Sheepflock in the Village of Oxynon, Greece.'),
        'citation': 'M. Popović, 2004',
        'category': ['vlachs']
    },
    {
        'src': 'vlachs_3.png',
        'description': _('A Sheepflock in the Village of Oxynon, Greece.'),
        'citation': 'M. Popović, 2004',
        'category': ['vlachs']
    },
    {
        'src': 'vlachs_4.png',
        'description':
            _('Nomadic Infrastructure in the Historical '
              'Region of Macedonia (14th Cent.)'),
        'citation':
            'Department of Geography and Reginal Research, '
            'University of Vienna, 2014',
        'category': ['vlachs']
    },
    {
        'src': 'vlachs_5.png',
        'description':
            _('The Winter Pastures in the Historical Region of '
              'Macedonia (14th Cent.)'),
        'citation': 'M. Popović',
        'category': ['vlachs']
    },
    {
        'src': 'vlachs_6.png',
        'description':
            _('The Summer Pastures in the Historical Region of '
              'Macedonia (14th Cent.)'),
        'citation': 'M. Popović',
        'category': ['vlachs']
    },
    {
        'src': 'vlachs_7.png',
        'description':
            _('The Distribution of Vlach Temporary Settlements (Katuni) in '
              'the Historical Region of Macedonia (14th Cent.)'),
        'citation': 'M. Popović',
        'category': ['vlachs']
    },
    {
        'src': 'vlachs_8.png',
        'description':
            _('The Source-Based Presence of Vlachs in the Historical '
              'Region of Macedonia (14th Cent.)'),
        'citation': 'M. Popović',
        'category': ['vlachs']
    },
]

project_vlachs = {
    'acronym': 'vlachs',
    'title': _(
        'The Ethnonym of the Vlachs in the Written Sources and the Toponymy '
        'in the Historical Region of Macedonia (11th-16th Cent.)'),
    'host_institutes': [institutes['abf']],
    'funded_by': [institutes['oead']],
    'project_number': 'MK 03/2016',
    'pi': ['Mihailo Popović (Vienna)', 'Toni Filiposki (Skopje)'],
    'cooperation': '',
    'employees': [
        'Boban Petrovski (Skopje)',
        'Nikola Minov (Skopje)',
        'Vladimir Kuhar (Skopje)',
        'Boban Gjorgjievski (Skopje)',
        'Jelena Nikić (Vienna)',
        'David Schmid (Vienna)',
    ],
    'begin': get_dates_formatted(2016, 7, 1),
    'end': get_dates_formatted(2018, 6, 30),
    'description': [
        _('vlachs_description_1'),
        _('vlachs_description_2')],
    'results': results,
    'icon': 'vlachs_icon.jpg',
    'images': images,
    'videos': [],
    'oaID': '8247',
}
