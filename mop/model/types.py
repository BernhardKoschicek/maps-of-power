from dataclasses import dataclass
from typing import Any, Dict, Optional, List
from pydantic import BaseModel, Field


class TypeHierarchyEntryModel(BaseModel):
    label: str
    identifier: str
    descriptions: Optional[str] = None


class EntityTypeModel(BaseModel):
    id: int
    title: str
    isStandard: bool = Field(..., alias="isStandard")
    descriptions: Optional[str] = None
    typeHierarchy: Optional[List[TypeHierarchyEntryModel]] = Field(
        None, alias="typeHierarchy")
    unit: Optional[str] = None
    value: Optional[str] = None

    class Config:
        populate_by_name = True


@dataclass
class Types:
    label: str
    hierarchy: str
    value: Any
    unit: Optional[str]
    description: Any
    identifier: str
    root: str

    def __init__(self, data: Optional[Dict[str, Any]] = None, **kwargs: Any):
        if data is not None:
            self.label = data['label']
            self.hierarchy = data['hierarchy']
            self.value = data['value']
            self.unit = data.get('unit')
            self.description = data.get('descriptions', [])
            self.identifier = data['identifier'].rsplit('/', 1)[-1]
            self.root = self.hierarchy.split('>')[0].rstrip()
        else:
            self.label = kwargs.get('label', '')
            self.hierarchy = kwargs.get('hierarchy', '')
            self.value = kwargs.get('value')
            self.unit = kwargs.get('unit')
            self.description = kwargs.get('description', '')
            self.identifier = kwargs.get('identifier', '')
            self.root = kwargs.get('root', '')

    @classmethod
    def from_model(cls, m: EntityTypeModel) -> 'Types':
        hierarchy_labels = (
            [entry.label for entry in m.typeHierarchy]
            if m.typeHierarchy else [])
        hierarchy_str = " > ".join(hierarchy_labels)
        root_str = hierarchy_labels[0] if hierarchy_labels else m.title
        return cls(
            label=m.title,
            hierarchy=hierarchy_str,
            value=m.value,
            unit=m.unit,
            description=m.descriptions or "",
            identifier=str(m.id),
            root=root_str)
