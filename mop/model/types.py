from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class Types:
    label: str
    hierarchy: str
    value: Any
    unit: Optional[str]
    description: list[dict[str, Any]]
    identifier: str
    root: str

    def __init__(self, data: Dict[str, Any]):
        self.label = data['label']
        self.hierarchy = data['hierarchy']
        self.value = data['value']
        self.unit = data.get('unit')
        self.description = data.get('descriptions', [])
        self.identifier = data['identifier'].rsplit('/', 1)[-1]
        self.root = self.hierarchy.split('>')[0].rstrip()
