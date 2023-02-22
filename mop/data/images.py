from flask_babel import lazy_gettext as _

category_images = {
    'written_source': {
        'src': 'hand_urk_passau.png',
        'description': _('image_written_source_description'),
        'caption': _('image_written_source_caption'),
    },
    'ausgrabung': {
        'src': 'ausgrabung.jpg',
        'description': _('image_excavations_description'),
        'caption': _('image_excavations_caption'),
    },
    'tab': {
        'src': 'tab.jpg',
        'description': _('image_toponym_description'),
        'caption': _('image_toponym_caption'),
    },
    'landscape': {
        'src': 'landscape.jpg',
        'description': _('image_landscape_description'),
        'caption': _('image_landscape_caption'),
    }
}
