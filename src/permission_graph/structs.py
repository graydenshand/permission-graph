from dataclasses import dataclass
from enum import Enum
from typing import Self


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
    def vertex_id(self) -> str:
        return f"{self.vtype}:{self.id}"

    @classmethod
    def from_vertex_id(cls, vertex_id: str) -> Self:
        id = vertex_id.split(":")[-1]
        return cls(id)

    def __eq__(self, other: object) -> bool:
        return self.vertex_id == other.vertex_id


class Actor(Vertex):
    vtype = "actor"


class Group(Vertex):
    vtype = "group"


class Resource(Vertex):
    vtype = "resource"

    def __init__(self, id: str, resource_type: ResourceType | None = None):
        super().__init__(id)
        self.resource_type = resource_type


class Action(Vertex):
    vtype = "action"

    def __init__(self, id: str, resource: Resource):
        super().__init__(id)
        self.resource = resource

    @property
    def vertex_id(self) -> str:
        return f"{self.vtype}:{self.resource.id}:{self.id}"

    @classmethod
    def from_vertex_id(cls, vertex_id: str) -> Self:
        _, resource_id, id = vertex_id.split(":")
        resource = Resource(resource_id)
        return cls(id, resource)


def vertex_factory(vtype: str, vertex_id: str):
    vtype_map = {"actor": Actor, "resource": Resource, "action": Action, "group": Group}
    return vtype_map[vtype].from_vertex_id(vertex_id)


class EdgeType(Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    MEMBER_OF = "MEMBER_OF"


class TieBreakerPolicy(Enum):
    ANY_ALLOW = "ANY_ALLOW"
    ALL_ALLOW = "ALL_ALLOW"
