from flask_babel import lazy_gettext as _

from mop.data.institutes import institutes
from mop.util import get_dates_formatted


images = [{
    'src': 'idcew_1.jpg',
    'description':
        _('The Church of the Holy Trinity in Sopoćani Monastery in the 1970s'),
    'citation': _('Photograph Collection "Dipl. Kfm. Wolfgang Milan (1924-2015)"'),
    'category': ['idcew']
}, {
    'src': 'idcew_2.jpg',
    'description':
        _('The Apse of the Church of the Holy Trinity in Sopoćani Monastery in the 1970s'),
    'citation': _('Photograph Collection "Dipl. Kfm. Wolfgang Milan (1924-2015)"'),
    'category': ['idcew']
}, {
    'src': 'idcew_3.jpg',
    'description':
        _('The Church of the Annunciation of the Holy Mother of God in Gradac Monastery in the 1970s'),
    'citation': _('Photograph Collection "Dipl. Kfm. Wolfgang Milan (1924-2015)"'),
    'category': ['idcew']
}, {
    'src': 'idcew_4.jpg',
    'description': _('The Church of the Annunciation of the Holy Mother of God in Gradac Monastery in 2007'),
    'citation': 'M.radosavljevic, 2007 <a href="https://creativecommons.org/licenses/by-sa/3.0/deed.en" target="_blank">CC BY-SA 3.0</a>',
    'category': ['idcew']
},
]

project_idcew = {
    'acronym': 'idcew',
    'title': _(
        'Helen – a Catholic Noblewoman, Serbian Queen and Interreligious '
        'Donor connecting East and West in the 13th/14th Centuries (IDCEW)'),
    'website': '',
    'host_institutes':
        [institutes['abf'], institutes['oeai'], institutes['bg_uni']],
    'funded_by': [institutes['oead']],
    'project_number': 'RS 08/2024',
    'pi': [
        f'Mihailo Popović ({_("Vienna")})',
        f'Branka Vranešević ({_("Belgrade")})'],
    'cooperation': [],
    'employees': [
        f'Moisés Hernández Cordero ({_("Vienna")})',
        f'Vladimir Simić ({_("Belgrade")})',
        f'Žarko Vujošević ({_("Belgrade")})'],
    'begin': get_dates_formatted(2024, 7, 1),
    'end': get_dates_formatted(2025, 6, 30),
    'description': [
        _('idcew_description_1'),
        _('idcew_description_2')
    ],
    'results': '',
    'icon': '',
    'images': images,
    'videos': [],
    'oaID': '135263',
}
