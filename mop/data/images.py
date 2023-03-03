from flask_babel import lazy_gettext as _

category_images = {
    'written_source': {
        'src': 'rilska-gramota.jpg',
        'description': _('image_written_source_description'),
        'caption': _('image_written_source_caption'),
        'citation':
            'https://commons.wikimedia.org/wiki/File:Rilska-gramota.jpg'
    },
    'excavation': {
        'src': 'ausgrabung.jpg',
        'description': _('image_excavations_description'),
        'caption': _('image_excavations_caption'),
        'citation': ''
    },
    'toponym': {
        'src': 'tab.jpg',
        'description': _('image_toponym_description'),
        'caption': _('image_toponym_caption'),
        'citation': ''
    },
    'landscape': {
        'src': 'hermitage.jpg',
        'description': _('image_landscape_description'),
        'caption': _('image_landscape_caption'),
        'citation': 'Mihailo St. Popović, 2021'
    }
}
