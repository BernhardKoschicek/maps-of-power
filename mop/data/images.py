from flask_babel import lazy_gettext as _

category_images = {
    'written_source': {
        'src': 'rilska-gramota.png',
        'description': _('image_written_source_description'),
        'caption': _('image_written_source_caption'),
        'citation':
            'https://commons.wikimedia.org/wiki/File:Rilska-gramota.jpg'
    },
    'excavation': {
        'src': 'doclea.png',
        'description': _('image_excavations_description'),
        'caption': _('image_excavations_caption'),
        'citation': 'Mihailo St. Popović, 2021'
    },
    'toponym': {
        'src': 'map.png',
        'description': _('image_toponym_description'),
        'caption': _('image_toponym_caption'),
        'citation': 'https://www.landkartenarchiv.de/'
    },
    'landscape': {
        'src': 'kotor_bay.png',
        'description': _('image_landscape_description'),
        'caption': _('image_landscape_caption'),
        'citation': 'Mihailo St. Popović, 2021'
    }
}
