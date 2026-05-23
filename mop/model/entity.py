from dataclasses import dataclass, field
import os
from typing import Any, Optional, List, Dict
from pydantic import BaseModel, Field

from mop.model.types import Types, EntityTypeModel
from mop.model.util import split_date_string, format_date, uc_first
from mop.model.api_calls import get_entity_presentation


# --- Pydantic Models for API Response ---

class TimeRangeSubModel(BaseModel):
    earliest: Optional[str] = None
    latest: Optional[str] = None
    comment: Optional[str] = None


class TimeRangeModel(BaseModel):
    start: Optional[TimeRangeSubModel] = None
    end: Optional[TimeRangeSubModel] = None


class ExternalReferenceModel(BaseModel):
    id: Optional[str] = None
    identifier: Optional[str] = None
    referenceSystem: Optional[str] = Field(None, alias="referenceSystem")
    referenceURL: Optional[str] = Field(None, alias="referenceURL")
    resolverURL: Optional[str] = Field(None, alias="resolverURL")
    type: Optional[str] = None

    class Config:
        populate_by_name = True


class PresentationFileModel(BaseModel):
    id: int
    title: str
    license: Optional[str] = None
    licenseHolder: Optional[str] = Field(None, alias="licenseHolder")
    mimetype: str
    url: str
    publicShareable: Optional[bool] = Field(None, alias="publicShareable")
    IIIFBasePath: Optional[str] = Field(None, alias="IIIFBasePath")
    IIIFManifest: Optional[str] = Field(None, alias="IIIFManifest")
    creator: Optional[str] = None
    fromSuperEntity: Optional[bool] = Field(None, alias="fromSuperEntity")

    class Config:
        populate_by_name = True


class PresentationReferenceModel(BaseModel):
    id: int
    systemClass: str = Field(..., alias="systemClass")
    title: str
    type: Optional[str] = None
    typeId: Optional[int] = Field(None, alias="typeId")
    citation: str
    pages: Optional[str] = None

    class Config:
        populate_by_name = True


class RelationTypeModel(BaseModel):
    property: str
    type: Optional[str] = None
    description: Optional[str] = None
    when: Optional[TimeRangeModel] = None
    relationTo: int = Field(..., alias="relationTo")

    class Config:
        populate_by_name = True


class RelatedEntityModel(BaseModel):
    id: int
    systemClass: str = Field(..., alias="systemClass")
    viewClass: Optional[str] = Field(None, alias="viewClass")
    title: Optional[str] = Field("", alias="title")
    description: Optional[str] = None
    aliases: List[str] = Field(default_factory=list)
    geometries: Optional[Dict[str, Any]] = None
    when: Optional[TimeRangeModel] = None
    relationTypes: List[RelationTypeModel] = Field(default_factory=list, alias="relationTypes")
    standardType: Optional[Dict[str, Any]] = Field(None, alias="standardType")

    class Config:
        populate_by_name = True


class PresentationViewModel(BaseModel):
    id: int
    systemClass: str = Field(..., alias="systemClass")
    viewClass: str = Field(..., alias="viewClass")
    title: str
    description: Optional[str] = None
    aliases: List[str] = Field(default_factory=list)
    externalReferenceSystems: Optional[List[ExternalReferenceModel]] = Field(None, alias="externalReferenceSystems")
    files: Optional[List[PresentationFileModel]] = None
    geometries: Optional[Dict[str, Any]] = None
    references: Optional[List[PresentationReferenceModel]] = None
    relations: Dict[str, List[RelatedEntityModel]] = Field(default_factory=dict)
    types: Optional[List[EntityTypeModel]] = None
    when: Optional[TimeRangeModel] = None

    class Config:
        populate_by_name = True


# --- Helper functions for parsing ---

def format_time_range(time_range: Optional[TimeRangeModel]) -> tuple[Optional[str], Optional[str]]:
    if not time_range:
        return None, None
    begin = None
    end = None
    if time_range.start:
        begin_from = split_date_string(time_range.start.earliest)
        begin_to = split_date_string(time_range.start.latest)
        begin = format_date(begin_from, begin_to)
    if time_range.end:
        end_from = split_date_string(time_range.end.earliest)
        end_to = split_date_string(time_range.end.latest)
        end = format_date(end_from, end_to)
    return begin, end


def get_geometry_data(geometries: Optional[Dict[str, Any]]) -> Optional[Any]:
    if not geometries:
        return None
    if isinstance(geometries, dict) and geometries.get('type') == 'GeometryCollection':
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
    raw_begin: Optional[str] = None
    raw_end: Optional[str] = None


@dataclass
class Entity:
    id_: str
    name: str
    description: str
    system_class: str
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

    def __init__(self, data: Optional[Dict[str, Any]] = None, **kwargs: Any) -> None:
        if data is not None:
            # Legacy initialization from standard list endpoints (/view_class)
            self.id_ = str(data['@id'].rsplit('/', 1)[-1])
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
            self.geometry = None
        else:
            # Keyword initialization from factories
            self.id_ = str(kwargs.get('id_'))
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

    @staticmethod
    def get_description(data: Optional[List[Dict[str, Any]]]) -> str:
        return [i['value'] for i in data][0] if data else ''

    @classmethod
    def get_entity_from_oa(cls, id_: int) -> 'Entity':
        raw_data = get_entity_presentation(id_)
        model = PresentationViewModel.model_validate(raw_data)
        return cls.from_model(model)

    @classmethod
    def from_model(cls, m: PresentationViewModel) -> 'Entity':
        # 1. Format dates
        begin, end = format_time_range(m.when)

        # 2. Parse types
        types_list = [Types.from_model(t) for t in m.types] if m.types else None

        # 3. Parse depictions (files)
        depictions_list = []
        if m.files:
            for f in m.files:
                dep = Depiction(
                    link=str(f.id),
                    title=f.title,
                    license=f.license or "",
                    url=f.url,
                    creator=f.creator or "",
                    license_holder=f.licenseHolder or "",
                    public_shareable=f.publicShareable if f.publicShareable is not None else True,
                    mimetype=f.mimetype,
                    iiif_base_path=f.IIIFBasePath or "",
                    iiif_manifest=f.IIIFManifest or "",
                    extension=os.path.splitext(f.url.rsplit('/', 1)[-1])[1] if f.url else "",
                    description=""
                )
                depictions_list.append(dep)

        # 4. Parse external links
        links_list = []
        if m.externalReferenceSystems:
            for ref in m.externalReferenceSystems:
                links_list.append(
                    ExternalLink(
                        identifier=ref.referenceURL or ref.identifier or "",
                        referenceSystem=ref.referenceSystem or ""
                    )
                )

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
        if m.references:
            for ref in m.references:
                references.append(
                    Relation(
                        relation_to_id=str(ref.id),
                        label=ref.title,
                        system_class=uc_first(ref.systemClass.replace('_', ' ')),
                        begin=None,
                        end=None,
                        type=ref.type,
                        description=ref.citation,
                        geometry=None
                    )
                )

        # Populate all other relations
        for sys_class_key, rel_list in m.relations.items():
            for rel in rel_list:
                rel_begin, rel_end = format_time_range(rel.when)
                rel_type = ", ".join([rt.type for rt in rel.relationTypes if rt.type]) if rel.relationTypes else None
                raw_begin_val = rel.when.start.earliest if (rel.when and rel.when.start) else None
                raw_end_val = rel.when.end.latest if (rel.when and rel.when.end) else None

                rel_obj = Relation(
                    relation_to_id=str(rel.id),
                    label=rel.title,
                    system_class=uc_first(rel.systemClass.replace('_', ' ')),
                    begin=rel_begin,
                    end=rel_end,
                    type=rel_type,
                    description=rel.description or "",
                    geometry=get_geometry_data(rel.geometries),
                    raw_begin=raw_begin_val,
                    raw_end=raw_end_val
                )

                sc = rel.systemClass.lower()
                if sc in ['place', 'feature', 'stratigraphic_unit']:
                    places.append(rel_obj)
                elif sc in ['group', 'person']:
                    actors.append(rel_obj)
                elif sc in ['acquisition', 'activity', 'event', 'move', 'production', 'creation']:
                    events.append(rel_obj)
                elif sc in ['artifact', 'human_remains']:
                    artifacts.append(rel_obj)
                elif sc == 'source':
                    sources.append(rel_obj)
                elif sc == 'source_translation':
                    source_translations.append(rel_obj)
                elif sc == 'administrative_unit':
                    administrative_unit.append(rel_obj)
                elif sc in ['bibliography', 'edition', 'external_reference', 'reference_system', 'file']:
                    if sc in ['bibliography', 'edition', 'external_reference']:
                        # Avoid duplicates from top-level references
                        pass
                    else:
                        others.append(rel_obj)
                else:
                    others.append(rel_obj)

        if places:
            mapped_relations['places'] = places
        if actors:
            mapped_relations['actors'] = actors
        if events:
            mapped_relations['events'] = events
        if artifacts:
            mapped_relations['artifacts'] = artifacts
        if references:
            mapped_relations['references'] = references
        if sources:
            mapped_relations['sources'] = sources
        if source_translations:
            mapped_relations['source_translations'] = source_translations
        if administrative_unit:
            mapped_relations['administrative_unit'] = administrative_unit
        if others:
            mapped_relations['others'] = others

        begin_from = m.when.start.earliest if (m.when and m.when.start) else None
        end_from = m.when.end.latest if (m.when and m.when.end) else None

        return cls(
            id_=str(m.id),
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
            geometry=get_geometry_data(m.geometries),
            begin_from=begin_from,
            end_from=end_from
        )
