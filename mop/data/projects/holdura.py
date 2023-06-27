from flask_babel import lazy_gettext as _

from mop.data.institutes import institutes
from mop.util import get_dates_formatted, youtube_iframe

results = {
    'text': [
        _('holdura_result_text_1')
    ],
    'list': [],
    'icons': [{
        'label': _("relief map of Montenegro"),
        'link': 'https://tib.oeaw.ac.at/static/3dhop/relief.html',
        'file': None,
        'icon': 'bi-image-alt',
    }, {
        'label': _('explore TIB Balkans data'),
        'link': 'https://tib.oeaw.ac.at/balkan/digital/explore',
        'file': None,
        'icon': 'bi-stack',
    }]
}

images = [{
    'src': 'holdura_doclea_1.jpg',
    'description': _('Bird\'s eye view of the Doclea archaeological '
                     'excavation, A: Basilica A, B: Basilica B and'
                     ' cruciform church, Republic of Montenegro'),
    'citation': 'L. Neugebauer, 2021',
    'category': ['holdura']
}, {
    'src': 'holdura_doclea_2.jpg',
    'description': _('Bird\'s eye view of the Doclea archaeological '
                     'excavation, the western part of the city in '
                     'the foreground, Republic of Montenegro'),
    'citation': 'L. Neugebauer, 2021',
    'category': ['holdura']
}, {
    'src': 'holdura_sveti_nikola.jpg',
    'description': _('The monastery of Sveti Nikola Vranjina (in the '
                     'centre of the picture) on Lake Skadar, '
                     'Republic of Montenegro'),
    'citation': 'B. Koschiček-Krombholz, 2021',
    'category': ['holdura']
}, {
    'src': 'holdura_ratac.jpg',
    'description': _('The former Latin (Catholic) monastery of Ratac '
                     'from the 12th/13th century near the town '
                     'of Bar, Republic of Montenegro.'),
    'citation': 'M. St. Popović, 2021',
    'category': ['holdura']
}]

project_holdura = {
    'acronym': 'holdura',
    'title': _(
        'Beyond East and West: Geocommunicating the Sacred Landscapes '
        'of "Duklja" and "Raška" through Space and Time (11th-14th Cent.)'),
    'funded_by': [institutes['fwf'], institutes['dfg']],
    'project_number': 'I 4330-G',
    'pi': ['Mihailo Popović'],
    'cooperation': [
        'Mag. Markus Breier', 'Lukas Neugebauer, BSc MSc',
        'Florian Korn, BSc MSc', 'Dipl.-Ing. Leonhard Kreil-Brunauer',
        'Ass. Prof. Dr. Branka Vranešević'],
    'employees': [
        'Dorota Vargová', 'Bernhard Koschiček-Krombholz', 'David Schmid'],
    'begin': get_dates_formatted(2020, 3, 1),
    'end': get_dates_formatted(2023, 8, 31),
    'description': [
        _('holdura_description_1'),
        _('holdura_description_2'),
        _('holdura_description_3'),
        _('holdura_description_4'),
        _('holdura_description_5'),
        _('holdura_description_6'),
        _('holdura_description_7'),
    ],
    'results': results,
    'icon': 'holdura_icon.jpg',
    'images': images,
    'videos': [
        youtube_iframe('https://www.youtube-nocookie.com/embed/Nhdx2OeWkN8')],
    'part': 'balkan',
    'oaID': 117730,
}
