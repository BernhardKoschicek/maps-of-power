from flask_babel import lazy_gettext as _

from mop.data.institutes import institutes
from mop.util import get_dates_formatted

images = [{
    'src': 'barbyz_1.jpg',
    'description': _('Surveying in North Macedonia'),
    'citation': 'Marka Tomić',
    'category': ['barbyz_10-13']
}, {
    'src': 'barbyz_2.jpg',
    'description': _('Surveying in North Macedonia'),
    'citation': 'Marka Tomić',
    'category': ['barbyz_10-13']
}, {
    'src': 'barbyz_3.jpg',
    'description': _('Surveying in North Macedonia'),
    'citation': 'Marka Tomić',
    'category': ['barbyz_10-13']
}, {
    'src': 'barbyz_4.jpg',
    'description': _('Surveying in North Macedonia'),
    'citation': 'Marka Tomić',
    'category': ['barbyz_10-13']
}, {
    'src': 'barbyz_5.jpg',
    'description': _('Surveying in North Macedonia'),
    'citation': 'Marka Tomić',
    'category': ['barbyz_10-13']
}]

project_barbyz = {
    'acronym': 'barbyz_10-13',
    'title': _(
        'From Barbarians to Christians and Rhomaioi. The Process of '
        'Byzantinization in the Central Balkans (late 10th – mid-13th '
        'century)'),
    'host_institutes': [institutes['sasa']],
    'funded_by': [institutes['sfrs']],
    'project_number': '7748349',
    'pi': ['Bojana Krsmanović'],
    'cooperation': [
        'Miloš Živković, Assistant professor, Faculty of Philosophy – '
        'University of Belgrade'],
    'employees': [
        'Predrag Komatina',
        'Stanoje Bojanin',
        'Ljubomir Milanović',
        'Maja Nikolić',
        'Marka Tomić',
        'Jovana Šijaković',
        'Miloš Cvetković',
        'Tamara Ilić',
        'Bojana Pavlović',
        'Vladan Zdravković'],
    'begin': get_dates_formatted(2022, 1, 15),
    'end': get_dates_formatted(2025, 1, 14),
    'description': [
        _('barbyz_description_1'),
        _('barbyz_description_2'),
        _('barbyz_description_3'),
        _('barbyz_description_4'),
        _('barbyz_description_5'),
        _('barbyz_description_6'),
    ],
    'results': '',
    'icon': '',
    'images': images,
    'videos': '',
    'oaID': '',
}
