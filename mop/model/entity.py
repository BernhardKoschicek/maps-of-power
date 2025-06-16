import os
from typing import Any, Optional

from mop.model.types import Types
from mop.model.util import split_date_string, format_date, uc_first
from mop.model.api_calls import get_entity


class Depiction:
    def __init__(self, data: dict[str, Any]):
        self.link = data['@id']
        self.title = data['title']
        self.license = data['license']
        self.url = data['url']
        self.creator = data['creator']
        self.license_holder = data['licenseHolder']
        self.public_shareable = data['publicShareable']
        self.mimetype = data['mimetype']
        self.iiif_base_path = data['IIIFBasePath']
        self.iiif_manifest = data['IIIFManifest']
        self.extension = os.path.splitext(self.url.rsplit('/', 1)[-1])[1]


class Entity:
    def __init__(self, data: dict[str, Any]) -> None:
        self.id_ = data['@id'].rsplit('/', 1)[-1]
        self.name = data['properties']['title']
        self.description = self.get_description(data['descriptions'])
        self.system_class = uc_first(data['systemClass'].replace('_', ' '))
        self.types = self.get_types(data['types']) if 'types' in data else None
        self.alias = self.get_alias(data['names']) if 'names' in data else None
        self.relations = data['relations'] if 'relations' in data else None
        self.depictions = self.get_depiction(data['depictions']) \
            if 'depictions' in data else None
        self.links = data['links'] if 'links' in data else None
        self.begin_from = None
        self.begin_to = None
        self.begin_comment = None
        self.end_from = None
        self.end_to = None
        self.begin = None
        self.end = None
        self.geometry = self.handling_geometry(data)
        if 'when' in data:
            self.begin_from = split_date_string(
                data['when']['timespans'][0]['start']['earliest'])
            self.begin_to = split_date_string(
                data['when']['timespans'][0]['start']['latest'])
            self.end_from = split_date_string(
                data['when']['timespans'][0]['end']['earliest'])
            self.end_to = split_date_string(
                data['when']['timespans'][0]['end']['latest'])
            self.begin = format_date(self.begin_from, self.begin_to)
            self.end = format_date(self.end_from, self.end_to)

    @staticmethod
    def get_entity_from_oa(id_: int):
        return Entity(get_entity(id_))

    @staticmethod
    def get_alias(data: list[dict[str, str]]) -> str:
        return ', '.join(map(str, [alias['alias'] for alias in data])) \
            if data else ''

    @staticmethod
    def get_types(data: list[dict[str, Any]]) -> Optional[list[Types]]:
        return [Types(types) for types in data] if data else None

    @staticmethod
    def get_depiction(data: list[dict[str, Any]]) -> Optional[list[Depiction]]:
        return [Depiction(depiction) for depiction in data] if data else None

    # @staticmethod
    # def get_relations(
    # data: list[dict[str, Any]]) -> Optional[list[Relation]]:
    #     return [Relation(relation) for relation in data] if data else None

    @staticmethod
    def get_description(data: list[dict[str, Any]]) -> Optional[list[str]]:
        return [i['value'] for i in data][0] if data else None

    @staticmethod
    def handling_geometry(
            data: dict[str, Any]) -> Optional[list[dict[str, Any]]]:
        if geometry := data.get('geometry'):
            if geometry['type'] == 'GeometryCollection':
                return geometry['geometries']
            return geometry
        return None


class Relation(Entity):
    def __init__(self, data: dict[str, Any]):
        super().__init__(data)
        self.label = data['label']
        self.relation_to_id = data['relationTo'].rsplit('/', 1)[-1]
        self.relation_to = data['relationTo']
        self.relation_type = data['relationType']
        self.relation_system_class = data['relationSystemClass']
        self.relation_description = data['relationDescription']
        self.type = data['type']
