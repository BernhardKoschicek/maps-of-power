from flask_babel import lazy_gettext as _

category_images = {
    'written_source': {
        'src': 'images/test_images/hand_urk_passau.png',
        'description': _('image_written_source_description'),
        'caption': _('image_written_source_caption'),
    },
    'ausgrabung': {
        'src': 'images/test_images/ausgrabung.jpg',
        'description': _('image_excavations_description'),
        'caption': _('image_excavations_caption'),
    },
    'tab': {
        'src': 'images/test_images/tab.jpg',
        'description': _('image_toponym_description'),
        'caption': _('image_toponym_caption'),
    },
    'landscape': {
        'src': 'images/test_images/landscape.jpg',
        'description': _('image_landscape_description'),
        'caption': _('image_landscape_caption'),
    }
}
