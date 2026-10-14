from dataclasses import dataclass, field
import os
from typing import Any, Dict, List, Optional
from flask import request
from pydantic import BaseModel, ConfigDict, Field

from mop.model.types import Types, EntityTypeModel
from mop.model.util import (
    format_date, split_date_string, uc_first, uuid_to_base62)
from mop.model.api_calls import get_entity_presentation

# --- Pydantic Models for API Response ---


class TimeRangeSubModel(BaseModel):
    earliest: str | None = None
    latest: str | None = None
    comment: str | None = None


class TimeRangeModel(BaseModel):
    start: TimeRangeSubModel | None = None
    end: TimeRangeSubModel | None = None


class ExternalReferenceModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str | None = None
    identifier: str | None = None
    referenceSystem: str | None = Field(None, alias="referenceSystem")
    referenceURL: str | None = Field(None, alias="referenceURL")
    resolverURL: str | None = Field(None, alias="resolverURL")
    type: str | None = None


class PresentationFileModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int
    title: str
    license: str | None = None
    licenseHolder: str | None = Field(None, alias="licenseHolder")
    mimetype: str
    url: str
    publicShareable: bool | None = Field(None, alias="publicShareable")
    IIIFBasePath: str | None = Field(None, alias="IIIFBasePath")
    IIIFManifest: str | None = Field(None, alias="IIIFManifest")
    creator: str | None = None
    fromSuperEntity: bool | None = Field(None, alias="fromSuperEntity")
    mainImage: bool | None = Field(None, alias="mainImage")


class PresentationReferenceModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int
    systemClass: str = Field(..., alias="systemClass")
    title: str
    type: str | None = None
    typeId: int | None = Field(None, alias="typeId")
    citation: str | None = None
    pages: str | None = None


class RelationTypeModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    property: str
    type: str | None = None
    description: str | None = None
    when: TimeRangeModel | None = None
    relationTo: int = Field(..., alias="relationTo")


class RelatedEntityModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int
    systemClass: str = Field(..., alias="systemClass")
    viewClass: str | None = Field(None, alias="viewClass")
    title: str | None = Field("", alias="title")
    description: str | None = None
    aliases: list[str] = Field(default_factory=list)
    geometries: dict[str, Any] | None = None
    when: TimeRangeModel | None = None
    relationTypes: list[RelationTypeModel] = Field(
        default_factory=list, alias="relationTypes")
    standardType: dict[str, Any] | None = Field(None, alias="standardType")


class PresentationViewModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int
    uuid: str | None = None
    systemClass: str = Field(..., alias="systemClass")
    viewClass: str = Field(..., alias="viewClass")
    title: str
    description: str | None = None
    aliases: list[str] = Field(default_factory=list)
    externalReferenceSystems: list[ExternalReferenceModel] | None = Field(
        None, alias="externalReferenceSystems")
    files: list[PresentationFileModel] | None = None
    geometries: dict[str, Any] | None = None
    references: list[PresentationReferenceModel] | None = None
    relations: dict[str, list[RelatedEntityModel]] = Field(
        default_factory=dict)
    types: list[EntityTypeModel] | None = None
    when: TimeRangeModel | None = None



# --- Helper functions for parsing ---


def format_time_range(
    time_range: Optional[TimeRangeModel]
) -> tuple[Optional[str], Optional[str]]:
    if not time_range:  # pragma: no cover
        return None, None
    begin = None
    end = None
    if time_range.start:  # pragma: no cover
        begin_from = split_date_string(time_range.start.earliest)
        begin_to = split_date_string(time_range.start.latest)
        begin = format_date(begin_from, begin_to)
    if time_range.end:  # pragma: no cover
        end_from = split_date_string(time_range.end.earliest)
        end_to = split_date_string(time_range.end.latest)
        end = format_date(end_from, end_to)
    return begin, end


def get_geometry_data(geometries: Optional[Dict[str, Any]]) -> Optional[Any]:
    if not geometries:
        return None
    if (isinstance(geometries, dict)
            and geometries.get('type') == 'GeometryCollection'):
        # pragma: no cover
        return geometries.get('geometries')
    return geometries


# --- Dataclasses used in Views & Templates ---


@dataclass
class Depiction:
    link: str
    title: str
    license: str
    url: str
    creator: str
    license_holder: str
    public_shareable: bool
    mimetype: str
    iiif_base_path: str
    iiif_manifest: str
    extension: str
    description: str = ""
    main_image: bool = False

    @property
    def iiif_thumbnail_url(self) -> str:
        if not self.iiif_base_path:
            return ""
        base, _ = os.path.splitext(self.iiif_base_path)
        return f"{base}.tiff/full/400,/0/default.jpg"


@dataclass
class ExternalLink:
    identifier: str
    referenceSystem: str


@dataclass
class Relation:
    relation_to_id: str
    label: str
    system_class: str
    begin: Optional[str]
    end: Optional[str]
    type: Optional[str]
    description: Optional[str]
    geometry: Optional[Any]
    properties: List[str] = field(default_factory=list)
    inverse: bool = False
    raw_begin: Optional[str] = None
    raw_end: Optional[str] = None


@dataclass
class Entity:
    id_: str
    name: str
    description: str
    system_class: str
    uuid: Optional[str] = None
    types: Optional[List[Types]] = None
    alias: Optional[str] = None
    relations: Optional[Dict[str, List[Relation]]] = None
    depictions: Optional[List[Depiction]] = None
    links: Optional[List[ExternalLink]] = None
    begin: Optional[str] = None
    end: Optional[str] = None
    geometry: Optional[Any] = None
    begin_from: Optional[str] = None
    end_from: Optional[str] = None

    def __init__(
            self,
            data: Optional[Dict[str, Any]] = None,
            **kwargs: Any) -> None:
        if data is not None:
            # Legacy initialization from standard list endpoints (/view_class)
            self.id_ = str(data['@id'].rsplit('/', 1)[-1])
            self.uuid = data.get('uuid')
            self.name = data['properties']['title']
            self.description = self.get_description(data.get('descriptions'))
            self.system_class = uc_first(data['systemClass'].replace('_', ' '))
            self.types = None
            self.alias = None
            self.relations = None
            self.depictions = None
            self.links = None
            self.begin = None
            self.end = None
            self.geometry = get_geometry_data(data.get('geometry'))
        else:
            # Keyword initialization from factories
            self.id_ = str(kwargs.get('id_'))
            self.uuid = kwargs.get('uuid')
            self.name = kwargs.get('name', '')
            self.description = kwargs.get('description', '')
            self.system_class = kwargs.get('system_class', '')
            self.types = kwargs.get('types')
            self.alias = kwargs.get('alias')
            self.relations = kwargs.get('relations')
            self.depictions = kwargs.get('depictions')
            self.links = kwargs.get('links')
            self.begin = kwargs.get('begin')
            self.end = kwargs.get('end')
            self.geometry = kwargs.get('geometry')

    @property
    def base62_id(self) -> Optional[str]:
        if self.uuid:
            try:
                return uuid_to_base62(self.uuid)
            except Exception:  # pragma: no cover
                return None
        return None

    @property
    def pid_url(self) -> Optional[str]:
        b62 = self.base62_id
        if b62:
            try:
                return f"{request.host_url.rstrip('/')}/id/{b62}"
            except Exception:  # pragma: no cover
                return f"/id/{b62}"
        return None

    @staticmethod
    def get_description(data: Optional[List[Dict[str, Any]]]) -> str:
        return [i['value'] for i in data][0] if data else ''

    @classmethod
    def get_entity_from_oa(
            cls, id_: int,
            api_path: Optional[str] = None) -> 'Entity':
        raw_data = get_entity_presentation(id_, api_path=api_path)
        model = PresentationViewModel.model_validate(raw_data)
        return cls.from_model(model)

    @classmethod
    def from_model(cls, m: PresentationViewModel) -> 'Entity':
        # 1. Format dates
        begin, end = format_time_range(m.when)

        # 2. Parse types
        types_list = ([Types.from_model(t)
                       for t in m.types] if m.types else None)

        # 3. Parse depictions (files)
        depictions_list = []
        if m.files:  # pragma: no cover
            for f in m.files:
                dep = Depiction(
                    link=str(f.id),
                    title=f.title,
                    license=f.license or "",
                    url=f.url,
                    creator=f.creator or "",
                    license_holder=f.licenseHolder or "",
                    public_shareable=f.publicShareable if
                    (f.publicShareable is not None) else True,
                    mimetype=f.mimetype,
                    iiif_base_path=f.IIIFBasePath or "",
                    iiif_manifest=f.IIIFManifest or "",
                    extension=os.path.splitext(f.url.rsplit('/', 1)[-1])[1]
                    if f.url else "",
                    description="",
                    main_image=(
                        f.mainImage if f.mainImage is not None else False))
                depictions_list.append(dep)

        # 4. Parse external links
        links_list = []
        if m.externalReferenceSystems:  # pragma: no cover
            for ref in m.externalReferenceSystems:
                links_list.append(
                    ExternalLink(
                        identifier=ref.referenceURL or ref.identifier or "",
                        referenceSystem=ref.referenceSystem or ""))

        # 5. Parse relations
        mapped_relations: Dict[str, List[Relation]] = {}
        places = []
        actors = []
        events = []
        artifacts = []
        references = []
        sources = []
        source_translations = []
        administrative_unit = []
        others = []

        # Populate literature references from the top-level references field
        if m.references:  # pragma: no cover
            for p_ref in m.references:
                references.append(
                    Relation(
                        relation_to_id=str(p_ref.id),
                        label=p_ref.title or "",
                        system_class=uc_first(
                            p_ref.systemClass.replace('_', ' ')),
                        begin=None,
                        end=None,
                        type=p_ref.type,
                        description=p_ref.citation,
                        geometry=None))

        # Populate all other relations
        for sys_class_key, rel_list in m.relations.items():
            for rel in rel_list:
                rel_begin, rel_end = format_time_range(rel.when)
                rel_type = ", ".join([
                    rt.type for rt in rel.relationTypes
                    if rt.type]) if rel.relationTypes else None
                raw_begin_val = (
                    rel.when.start.earliest if
                    (rel.when and rel.when.start) else None)
                raw_end_val = (
                    rel.when.end.latest if
                    (rel.when and rel.when.end) else None)
                properties = ([
                    rt.property for rt in rel.relationTypes
                    if rt.property] if rel.relationTypes else [])
                is_inverse = any(
                    p.split("_", 1)[0].endswith("i") for p in properties)

                rel_obj = Relation(
                    relation_to_id=str(rel.id),
                    label=rel.title or "",
                    system_class=uc_first(rel.systemClass.replace('_', ' ')),
                    begin=rel_begin,
                    end=rel_end,
                    type=rel_type,
                    description=rel.description or "",
                    geometry=get_geometry_data(rel.geometries),
                    properties=properties,
                    inverse=is_inverse,
                    raw_begin=raw_begin_val,
                    raw_end=raw_end_val)

                sc = rel.systemClass.lower()
                if sc in ['place', 'feature', 'stratigraphic_unit']:
                    places.append(rel_obj)
                elif sc in ['group', 'person']:
                    actors.append(rel_obj)
                elif sc in ['acquisition', 'activity', 'event', 'move',
                            'production', 'creation']:
                    events.append(rel_obj)
                elif sc in ['artifact', 'human_remains']:  # pragma: no cover
                    artifacts.append(rel_obj)
                elif sc == 'source':  # pragma: no cover
                    sources.append(rel_obj)
                elif sc in ['source_translation', 'text']:  # pragma: no cover
                    source_translations.append(rel_obj)
                elif sc == 'administrative_unit':  # pragma: no cover
                    administrative_unit.append(rel_obj)
                elif sc in ['bibliography', 'edition', 'external_reference',
                            'reference_system', 'file']:  # pragma: no cover
                    if sc in ['bibliography', 'edition', 'external_reference']:
                        # Avoid duplicates from top-level references
                        pass
                    else:
                        others.append(rel_obj)
                else:  # pragma: no cover
                    others.append(rel_obj)

        if places:  # pragma: no cover
            mapped_relations['places'] = places
        if actors:
            mapped_relations['actors'] = actors
        if events:
            mapped_relations['events'] = events
        if artifacts:  # pragma: no cover
            mapped_relations['artifacts'] = artifacts
        if references:
            mapped_relations['references'] = references
        if sources:  # pragma: no cover
            mapped_relations['sources'] = sources
        if source_translations:  # pragma: no cover
            mapped_relations['source_translations'] = source_translations
        if administrative_unit:  # pragma: no cover
            mapped_relations['administrative_unit'] = administrative_unit
        if others:  # pragma: no cover
            mapped_relations['others'] = others

        begin_from = (
            m.when.start.earliest if (m.when and m.when.start) else None)
        end_from = (m.when.end.latest if (m.when and m.when.end) else None)

        geometry = get_geometry_data(m.geometries)
        if not geometry:
            for rel_group in mapped_relations.values():
                for mapped_rel in rel_group:
                    if (mapped_rel.geometry
                            and any("P46" in p
                                    for p in mapped_rel.properties)):
                        geometry = mapped_rel.geometry
                        break
                if geometry:
                    break

        return cls(
            id_=str(m.id),
            uuid=m.uuid,
            name=m.title,
            description=m.description or "",
            system_class=uc_first(m.systemClass.replace('_', ' ')),
            types=types_list,
            alias=", ".join(m.aliases) if m.aliases else "",
            relations=mapped_relations,
            depictions=depictions_list,
            links=links_list,
            begin=begin,
            end=end,
            geometry=geometry,
            begin_from=begin_from,
            end_from=end_from)
