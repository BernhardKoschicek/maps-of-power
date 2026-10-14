from dataclasses import dataclass
from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class TypeHierarchyEntryModel(BaseModel):
    label: str
    identifier: str
    descriptions: str | None = None


class EntityTypeModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int
    title: str
    isStandard: bool = Field(..., alias="isStandard")
    descriptions: str | None = None
    typeHierarchy: list[TypeHierarchyEntryModel] | None = Field(
        None, alias="typeHierarchy")
    unit: str | None = None
    value: str | None = None



@dataclass
class Types:
    label: str
    hierarchy: str
    value: Any
    unit: str | None
    description: Any
    identifier: str
    root: str

    def __init__(self, data: dict[str, Any] | None = None, **kwargs: Any):
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
        hierarchy_labels = ([entry.label for entry in m.typeHierarchy]
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
