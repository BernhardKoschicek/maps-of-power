from flask_babel import lazy_gettext as _

from mop.data.institutes import institutes
from mop.util import get_dates_formatted

images = [
    {
        'src': 'tib_balkan_1.jpg',
        'description': _('The Monastery of Saint Naum on Lake Ohrid'),
        'citation': 'Johannes Koder, 1965',
        'category': ['tib_balkan']},
    {
        'src': 'tib_balkan_2.jpg',
        'description': _('The Monastery of Saint Naum on Lake Ohrid'),
        'citation': 'Mihailo Popović, 2017',
        'category': ['tib_balkan']},
    {
        'src': 'tib_balkan_3.jpg',
        'description': _('The Church of Sveti Jovan Kaneo in Ohrid'),
        'citation': 'Wolfgang Lanz, 1970',
        'category': ['tib_balkan']},
    {
        'src': 'tib_balkan_4.jpg',
        'description': _('The Church of Sveti Jovan Kaneo in Ohrid'),
        'citation': 'Mihailo Popović, 2008',
        'category': ['tib_balkan']},
    {
        'src': 'lada_niva_bonce.jpg',
        'description': _(
            'With archaeologist Prof. Dr. Viktor Lilčikj and his Lada Niva on '
            'the way to the site of Bonče, Republic of North Macedonia (2016)'),
        'citation': 'Mihailo St. Popović, TIB 16',
        'category': ['tib_balkan']},
    {
        'src': 'balkan_cartographie_koder.png',
        'description': _(
            'Processing schedule for the volumes of the TIB Balkan '
            '(Johannes Koder, 1960s, TIB Archive)'),
        'citation': 'Johannes Koder, TIB Archive',
        'category': ['tib_balkan']}]

project_tib_balkan = {
    'acronym': 'tib_balkan',
    'title': _('Reverse Engineering of the Tabula Imperii Byzantini Balkans'),
    'website': '/tib',
    'host_institutes': [institutes['abf']],
    'funded_by': [],
    'project_number': '',
    'pi': ['Mihailo Popović'],
    'cooperation': [],
    'employees': [
        'Bernhard Koschiček-Krombholz',
        'Moisés Hernández Cordero',
        'Elisabeth Charlotte Beer'],
    'former_employees': [
        'Dorota Vargová',
        'David Schmid',
        'Vratislav Zervan',
        'Veronika Polloczek'],
    'begin': get_dates_formatted(2025, 1, 1),
    'end': get_dates_formatted(2030, 12, 31),
    'description': [
        _('tib_balkan_description_1'),
        _('tib_balkan_description_2'),
        _('tib_balkan_description_3'),
        _('tib_balkan_intro_21st_century'),
        _('tib_balkan_surveys'),
        _('tib_balkan_cartography')],
    'results': '',
    'icon': 'tib_balkan_3.jpg',
    'images': images,
    'videos': '',
    'oaID': ['124486', '124485', '124487', '124484', '130938'],
    'api': 'mop'}
