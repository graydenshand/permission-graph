import uuid
from dataclasses import dataclass
from enum import Enum
from typing import Self

from pydantic import BaseModel, Field

# class ResourceType(BaseModel):
#     """A type of resource, with a fixed set of actions.

#     Attributes:
#         name: The name of the resource type
#         actions: A list of actions each resource of this type supports
#     """

#     name: str
#     actions: list[str]


class Vertex(BaseModel):
    """A vertex in the permission graph."""

    vtype: str
    name: str

    @property
    def id(self) -> str:
        return f"{self.vtype}:{self.name}"

    @classmethod
    def from_id(cls, vertex_id: str) -> str:
        """Return an instance of this class from a vertex id."""
        vtype, name = vertex_id.split(":")
        return cls(vtype=vtype, name=name)

    @staticmethod
    def factory(vertex_id: str, **kwargs) -> Self:
        """Return a vertex object given vtype and vertex_id.

        Args:
            vtype: The type of the vertex (`user`, `action`, `group`, `resource`)
            vertex_id: The id of the vertex
        """
        vtype_map = {"actor": Actor, "resource": Resource, "action": Action, "group": Group}
        vtype = vertex_id.split(":")[0]
        return vtype_map[vtype].from_id(vertex_id, **kwargs)


class ResourceType(Vertex):
    """A vertex type representing resource types."""

    vtype: str = Field(default="resource_type")
    actions: list[str]

    @classmethod
    def from_id(cls, vertex_id: str, actions):
        vtype, name = vertex_id.split(":")
        return cls(vtype=vtype, name=name, actions=actions)


class Actor(Vertex):
    """A vertex type representing an actor."""

    vtype: str = Field(default="actor")


class Group(Vertex):
    """A vertex type representing a group of Actors."""

    vtype: str = Field(default="group")


class Resource(Vertex):
    """A vertex type representing a resource."""

    vtype: str = Field(default="resource")
    resource_type: str

    @property
    def id(self) -> str:
        return f"{self.vtype}:{self.resource_type}:{self.name}"

    @classmethod
    def from_id(cls, vertex_id: str) -> Self:
        vtype, resource_type, name = vertex_id.split(":")
        return cls(vtype=vtype, resource_type=resource_type, name=name)


class Action(Vertex):
    """A vertex type representing an action on a resource."""

    vtype: str = Field(default="action")
    resource_type: str
    resource: str

    @property
    def id(self) -> str:
        return f"{self.vtype}:{self.resource_type}:{self.resource}:{self.name}"

    @classmethod
    def from_id(cls, vertex_id: str) -> Self:
        vtype, resource_type, resource, name = vertex_id.split(":")
        return cls(vtype=vtype, resource_type=resource_type, resource=resource, name=name)


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


class Effect(Enum):
    """The effect of a permission policy.

    Values

    - `ALLOW`: action is allowed
    - `DENY`: action is not allowed
    """

    ALLOW = "ALLOW"
    DENY = "DENY"


class PermissionPolicy(BaseModel):
    """A permission policy statement.

    PermissionPolicy objects represent a permission statement linking a user
    to an action.

    Attributes:
        action: The policy's action
        actor: The policy's actor
        resource: The resource being acted upon
        resourceType: The resource type of the resource being acted upon
    """

    action: Action
    actor: Actor
    group: Group | None
    resource: Resource
    resourceType: ResourceType
