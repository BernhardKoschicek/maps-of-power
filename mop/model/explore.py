from typing import Optional

from flask_babel import lazy_gettext as _

from mop.model.api_calls import get_view_class
from mop.model.entity import Entity

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

system_classes = {
    'acquisition': 'event',
    'activity': 'event',
    'administrative_unit': 'type',
    'artifact': 'artifact',
    'bibliography': 'reference',
    'creation': 'event',
    'edition': 'reference',
    'event': 'event',
    'external_reference': 'reference',
    'feature': 'place',
    'file': 'file',
    'group': 'actor',
    'human_remains': 'artifact',
    'move': 'event',
    'object_location': 'place',
    'person': 'actor',
    'place': 'place',
    'production': 'event',
    'reference_system': 'reference_system',
    'source': 'source',
    'source_translation': 'source_translation',
    'stratigraphic_unit': 'place',
    'type': 'type',
}


def get_oa_by_view_class(
        view: str,
        project_id: object) -> list[Optional[Entity]]:
    return [] if view not in view_classes else \
        [Entity(entry['features'][0])
         for entry in get_view_class(
            f'{view}?limit=0&'
            f'show=description&type_id={project_id}')]
