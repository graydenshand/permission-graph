from dataclasses import dataclass
from enum import Enum
from typing import Self


@dataclass
class ResourceType:
    """A type of resource, with a fixed set of actions.

    Attributes:
        name: The name of the resource type
        actions: A list of actions each resource of this type supports
    """

    name: str
    actions: list[str]


class Vertex:
    """Base class for graph Vertices."""

    vtype: str

    def __init__(self, name: str):
        """Initialize a vertex.

        A vertex is uniquely defined by it's vtype and name.

        Args:
            name: the name of the vertex
        """
        self.name = name

    @property
    def vertex_id(self) -> str:
        """Return the vertex_id of the vertex."""
        return f"{self.vtype}:{self.name}"

    @classmethod
    def from_vertex_id(cls, vertex_id: str) -> Self:
        """Return a Vertex object from vertex_id.

        Args:
            vertex_id: the id of the vertex to build from
        """
        name = vertex_id.split(":")[-1]
        return cls(name)

    def __eq__(self, other: object) -> bool:
        return self.vertex_id == other.vertex_id


class Actor(Vertex):
    """A vertex type representing an actor."""

    vtype = "actor"


class Group(Vertex):
    """A vertex type representing a group."""

    vtype = "group"


class Resource(Vertex):
    """A vertex type representing a resource."""

    vtype = "resource"

    def __init__(self, name: str, resource_type: ResourceType | None = None):
        """Initialize a resource.

        Args:
            name: The name of the resource
            resource_type: The type of the resource
        """
        super().__init__(name)
        self.resource_type = resource_type


class Action(Vertex):
    """A vertex type representing an action on a resource."""

    vtype = "action"

    def __init__(self, name: str, resource: Resource):
        """Initialize an action.

        Args:
            name: The name of the action
            resource: The resource this action operates on
        """
        super().__init__(name)
        self.resource = resource

    @property
    def vertex_id(self) -> str:
        return f"{self.vtype}:{self.resource.name}:{self.name}"

    @classmethod
    def from_vertex_id(cls, vertex_id: str) -> Self:
        _, resource_id, name = vertex_id.split(":")
        resource = Resource(resource_id)
        return cls(name, resource)


def vertex_factory(vtype: str, vertex_id: str) -> Vertex:
    """Return a vertex object given vtype and vertex_id.

    Args:
        vtype: The type of the vertex (`user`, `action`, `group`, `resource`)
        vertex_id: The id of the vertex
    """
    vtype_map = {"actor": Actor, "resource": Resource, "action": Action, "group": Group}
    return vtype_map[vtype].from_vertex_id(vertex_id)


class EdgeType(Enum):
    """Type for edges.

    Values

    - `ALLOW`: allow an actor to take an action
    - `DENY`: deny an actor from taking an action
    - `MEMBER_OF`: indicate membership in a collection
    """

    ALLOW = "ALLOW"
    DENY = "DENY"
    MEMBER_OF = "MEMBER_OF"


class TieBreakerPolicy(Enum):
    """Policy for breaking ties in permissions graph.

    Values

    - `ANY_ALLOW`: allow if any of the candidate paths allow the action
    - `ALL_ALLOW`: allow only if all of the candidate paths allow the action
    """

    ANY_ALLOW = "ANY_ALLOW"
    ALL_ALLOW = "ALL_ALLOW"
