from datetime import datetime
from typing import Any, Union, Optional

from flask import url_for
from flask_babel import lazy_gettext as _

from mop.model.entity import Relation
from mop.model.types import Types
from mop.model.util import flatten_list_and_remove_duplicates
from mop import app


def get_dates_formatted(year: int, month: int, day: int) -> str:
    return datetime(year, month, day).strftime('%d.%m.%Y')


def get_table_dates_formatted(year: int, month: int, day: int) -> str:
    return datetime(year, month, day).strftime('%Y/%m/%d')


def youtube_iframe(link_: str) -> str:
    return '<iframe width="560" height="315" ' \
           f'src="{link_}" ' \
           'title="YouTube video  player" ' \
           'allow="accelerometer; autoplay; clipboard-write;  ' \
           'encrypted-media; gyroscope; picture-in-picture" ' \
           'allowfullscreen></iframe>'


@app.context_processor
def inject_menu() -> dict[str, Any]:
    navbar = [
        {'name': _('about'), 'to': url_for('about')},
        {'name': _('projects'), 'to': url_for('projects')},
        {'name': _('atlas'), 'to': url_for('frontend')},
        {'name': 'histgeo', 'to': url_for('histgeo')},
        {'name': _('events'), 'to': url_for('events')},
        {'name': _('literature'), 'to': url_for('literature')}]
    return {'navbar': navbar}


def get_dict_entries_by_category(
        categories: Union[list[str], str],
        list_: list[dict[str, Any]]) -> list[dict[str, str]]:
    categories = [categories] if isinstance(categories, str) else categories
    return [entry for entry in list_
            if any(item in categories for item in entry['category'])]


def get_related_geoms(places: list[Relation]) -> list[dict[str, Any]]:
    geoms = []
    for place in places:
        geoms.append(place.geometry)
    return flatten_list_and_remove_duplicates(geoms)


def get_relation_entities(
        linked: list[dict[str, Any]],
        relations: list[dict[str, Any]]) -> list[Relation]:
    linked_entities = {}
    for entry in linked:
        linked_entities[entry['features'][0]['@id'].rsplit('/', 1)[-1]] \
            = entry['features'][0]
    for relation in relations:
        (linked_entities[relation['relationTo'].rsplit('/', 1)[-1]].
         update(relation))
    list_ = list(linked_entities.values())
    return [Relation(entity) for entity in list_]


def get_types_sorted(types: list[Types]) -> Optional[dict[str, Any]]:
    if not types:
        return None
    type_hierarchy: dict[str, Any] = {}
    for type_ in types:
        type_hierarchy.setdefault(type_.root, []).append(type_)
    return type_hierarchy


def get_relations(
        relations: list[Relation]) -> dict[str, list[Relation]]:
    relation_dict: dict[str, Any] = {}
    for relation in relations:
        match relation.relation_system_class:
            case 'file' | 'appellation' | \
                 'object_location' | 'reference_system':
                continue
            case 'type':
                relation_dict.setdefault('types', []).append(relation)
            case 'source':
                relation_dict.setdefault('sources', []).append(relation)
            case 'source_translation':
                (relation_dict.setdefault('source_translations', [])
                 .append(relation))
            case 'place' | 'feature' | 'stratigraphic_unit':
                relation_dict.setdefault('places', []).append(relation)
            case 'administrative_unit':
                relation_dict.setdefault('administrative_unit', []).append(
                    relation)
            case 'artifact' | 'human_remains':
                relation_dict.setdefault('artifacts', []).append(relation)
            case 'bibliography' | 'edition' | 'external_reference':
                relation_dict.setdefault('references', []).append(relation)
            case 'acquisition' | 'activity' | 'event' | 'move' | 'production':
                relation_dict.setdefault('events', []).append(relation)
            case 'group' | 'person':
                relation_dict.setdefault('actors', []).append(relation)
            case _:
                relation_dict.setdefault('others', []).append(relation)
    return relation_dict
