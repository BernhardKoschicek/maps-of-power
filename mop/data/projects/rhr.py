from flask_babel import lazy_gettext as _

from mop.data.institutes import institutes
from mop.util import get_dates_formatted

images = [{
    'src': 'rhr_louis_XIV.jpg',
    'description': _('The French King Louis XIV (1638-1715)'),
    'citation': 'Von Hyacinthe Rigaud - wartburg.edu[toter Link], Gemeinfrei, '
                'https://commons.wikimedia.org/w/index.php?curid=482613',
    'category': ['rhr']
}, {
    'src': 'rhr_eugene_ferdinand_victor_delacroix.jpg',
    'description': _('The Crusaders conquer Constantinople '
                     '(Eugène Delacroix, 1840)'),
    'citation': 'Par Eugène Delacroix — The Yorck Project (2002) 10.000'
                ' Meisterwerke der Malerei (DVD-ROM), distributed by '
                'DIRECTMEDIA Publishing GmbH. ISBN : 3936122202., '
                'Domaine public,'
                ' https://commons.wikimedia.org/w/index.php?curid=150159',
    'category': ['rhr']
}, {
    'src': 'rhr_01.jpg',
    'description': _('Reception of the Serbian King Petar I in Skopje in 1912,'
                     ' depicted in a French illustration'),
    'citation': '',
    'category': ['rhr']
}, {
    'src': 'rhr_02.jpg',
    'description': _('The Greek and Serbian pavilions at the World Exhibition'
                     ' in Paris in 1900'),
    'citation': '',
    'category': ['rhr']
},
]

project_rhr = {
    'acronym': 'rhr',
    'title': _(
        'The Reception History of Rumelia in Austria and France '
        '(Late 17th- Early 20th Centuries) (RHR)'),
    'website': '',
    'host_institutes': [institutes['univie'], institutes['om']],
    'funded_by': [institutes['oead']],
    'project_number': 'FR 06/2026',
    'pi': ['Mihailo Popović (Vienna)', 'Lilyana Yordanova (Paris)'],
    'cooperation': [],
    'employees': [
        'Veronika Polloczek (Wien)', 'Guillaume Bidaut (Paris)'],
    'begin': get_dates_formatted(2026, 1, 1),
    'end': get_dates_formatted(2027, 12, 31),
    'description': [
        _('rhr_description_1'),
        _('rhr_description_2')
    ],
    'results': '',
    'icon': 'holdura_icon.jpg',
    'images': images,
    'videos': [],
    'oaID': '',
}
