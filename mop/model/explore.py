from flask_babel import lazy_gettext as _

from model.api_calls import get_view_class
from model.entity import Entity

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


def get_oa_by_view_class(view: str, project_id: object) -> list[Entity]:
    if view not in view_classes:
        return []
    data = [Entity(entry['features'][0])
            for entry in get_view_class(
            f'{view}?limit=0&'
            f'show=description&type_id={project_id}')]
    return data
