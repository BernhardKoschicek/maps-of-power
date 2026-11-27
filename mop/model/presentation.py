"""Presentation helpers for entity GeoJSON geometries and timelines."""

from typing import Any

from mop.model.entity import Entity, Relation

_GEOMETRY_TYPES = {
    'Point', 'MultiPoint', 'LineString', 'MultiLineString',
    'Polygon', 'MultiPolygon', 'GeometryCollection'}
_IGNORED_TIMELINE_GROUPS = {
    'references', 'sources', 'source_translations', 'others'}


def normalize_and_inject_geojson(
        geojson_obj: Any,
        properties: dict[str, Any]) -> list[dict[str, Any]]:
    """Normalize GeoJSON payloads to Feature dicts with injected properties."""
    if not geojson_obj or not isinstance(geojson_obj, dict):
        return []
    obj_type = geojson_obj.get('type')
    features: list[dict[str, Any]] = []
    if obj_type == 'FeatureCollection':
        for item in geojson_obj.get('features', []):
            if isinstance(item, dict):
                f_copy = dict(item)
                f_copy['properties'] = dict(f_copy.get('properties') or {})
                f_copy['properties'].update(properties)
                features.append(f_copy)
    elif obj_type == 'Feature':
        f_copy = dict(geojson_obj)
        f_copy['properties'] = dict(f_copy.get('properties') or {})
        f_copy['properties'].update(properties)
        features.append(f_copy)
    elif obj_type in _GEOMETRY_TYPES:
        features.append({
            'type': 'Feature',
            'geometry': geojson_obj,
            'properties': dict(properties)})
    return features


def prepare_entity_geometries(
        entity: Entity,
        relations: dict[str, list[Relation]]) -> list[dict[str, Any]]:
    """Standardize entity.geometry in place and collect related features."""
    main_geometry = None
    if entity.geometry:
        features = normalize_and_inject_geojson(
            entity.geometry, {
                'title': entity.name,
                'description': entity.description or '',
                'systemClass': 'selected',
                'id': entity.id_})
        if features:
            main_geometry = {'type': 'FeatureCollection', 'features': features}
    entity.geometry = main_geometry

    related_places: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for rel_list in relations.values():
        for rel in rel_list:
            if rel.geometry and rel.relation_to_id not in seen_ids:
                seen_ids.add(rel.relation_to_id)
                features = normalize_and_inject_geojson(
                    rel.geometry, {
                        'title': rel.label,
                        'description': rel.description or '',
                        'systemClass': rel.system_class,
                        'id': rel.relation_to_id})
                related_places.extend(features)
    return related_places


def build_entity_timeline(
        entity: Entity,
        relations: dict[str, list[Relation]]) -> list[dict[str, Any]]:
    """Gather and chronologically sort entity lifecycle and relation events."""
    timeline_events: list[dict[str, Any]] = []
    for rel_group, rel_list in relations.items():
        if rel_group in _IGNORED_TIMELINE_GROUPS:
            continue
        for rel in rel_list:
            if rel.begin:
                sort_date = rel.raw_begin or rel.begin
                timeline_events.append({
                    'is_main': False,
                    'relation': rel,
                    'sort_date': sort_date,
                    'category': rel_group})

    if entity.begin:
        timeline_events.append({
            'is_main': True,
            'label': f'Start of {entity.name}',
            'type': 'Lifecycle Start',
            'begin': entity.begin,
            'sort_date': entity.begin_from or entity.begin,
            'system_class': entity.system_class})
    if entity.end:
        timeline_events.append({
            'is_main': True,
            'label': f'End of {entity.name}',
            'type': 'Lifecycle End',
            'begin': entity.end,
            'sort_date': entity.end_from or entity.end,
            'system_class': entity.system_class})

    timeline_events.sort(key=lambda x: str(x['sort_date'] or ''))
    return timeline_events
