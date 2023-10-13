from dataclasses import dataclass
from enum import Enum


@dataclass
class ResourceType:
    """Resource types"""

    name: str
    actions: list[str]


class Vertex:
    """Base class for graph Vertices."""

    vtype: str

    def __init__(self, id: str):
        self.id = id

    @property
    def vertex_id(self):
        return f"{self.vtype}:{self.id}"

    def __eq__(self, other: object) -> bool:
        return self.vertex_id == other.vertex_id


class User(Vertex):
    vtype = "user"


class Group(Vertex):
    vtype = "group"


class Resource(Vertex):
    vtype = "resource"

    def __init__(self, id: str, resource_type: ResourceType | None = None):
        super().__init__(id)
        self.resource_type = resource_type


class EdgeType(Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    MEMBER_OF = "MEMBER_OF"
