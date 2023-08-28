from flask_babel import lazy_gettext as _

view_classes = {
    'actor': {
        'display_name': _('Actors'),
        'description': _('Persons and Groups')},
    'place': {
        'display_name': _('Places'),
        'description': _('Physical places and their locations')},
    'event': {
        'display_name': _('Events'),
        'description': _('Linking places and actors')},
    'source': {
        'display_name': _('Sources'),
        'description': _('Documents, manuscripts, etc.')},
    'reference': {
        'display_name': _('References'),
        'description': _('Research literature')},
    'artifact': {
        'display_name': _('Artefacts'),
        'description': _('Physical objects')}}
