from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class TypeTree:
    id: int
    name: str
    description: str
    origin_id: int
    first: int
    last: int
    root: int
    subs: List[Dict[str, Any]]
    count: int
    count_subs: int
    category: str

    def __init__(self, data: Dict[str, Any]):
        self.id = data['id']
        self.name = data['name']
        self.description = data['description']
        self.origin_id = data['origin_id']
        self.first = data['first']
        self.last = data['last']
        self.root = data['root']
        self.subs = data['subs']
        self.count = data['count']
        self.count_subs = data['count_subs']
        self.category = data['category']
