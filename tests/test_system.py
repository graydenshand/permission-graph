"""System level tests."""
import pytest

from permission_graph import PermissionGraph
from permission_graph.backends.igraph import IGraphMemoryBackend
from permission_graph.structs import (
    Action,
    Actor,
    Group,
    Resource,
    ResourceType,
    TieBreakerPolicy,
)


@pytest.fixture
def igraph():
    backend = IGraphMemoryBackend()
    graph = PermissionGraph(backend=backend, tie_breaker_policy=TieBreakerPolicy.ANY_ALLOW)
    return graph


@pytest.mark.integration
def test_system(igraph):
    alice = Actor(name="Alice")
    igraph.add_actor(alice)

    admins = Group(name="Admins")
    igraph.add_group(admins)

    igraph.add_actor_to_group(alice, admins)

    document_type = ResourceType(name="Document", actions=["View", "Edit", "Share"])
    igraph.add_resource_type(document_type)

    document = Resource(name="MyDoc", resource_type="Document")
    igraph.add_resource(document)

    view_document = Action(name="View", resource_type="Document", resource="MyDoc")
    assert not igraph.action_is_authorized(alice, view_document)

    igraph.allow(admins, view_document)
    assert igraph.action_is_authorized(alice, view_document)

    igraph.deny(alice, view_document)
    assert not igraph.action_is_authorized(alice, view_document)

    igraph.revoke(alice, view_document)
    assert igraph.action_is_authorized(alice, view_document)

    # Conflicting dependencies
    public = Group(name="Public")
    igraph.add_group(public)
    igraph.add_actor_to_group(alice, public)
    igraph.deny(public, view_document)
    assert igraph.action_is_authorized(alice, view_document)

    # Permission propagation
    directory_type = ResourceType(name="Directory", actions=["View", "Create", "Share"])
    igraph.add_resource_type(directory_type)
    directory = Resource(name="Home", resource_type="Directory")
    igraph.add_resource(directory)

    bob = Actor(name="Bob")
    igraph.add_actor(bob)
    assert not igraph.action_is_authorized(bob, Action(name="Share", resource_type="Document", resource="MyDoc"))

    igraph.allow(
        Action(name="Share", resource_type="Directory", resource="Home"),
        Action(name="Share", resource_type="Document", resource="MyDoc"),
    )
    igraph.allow(bob, Action(name="Share", resource_type="Directory", resource="Home"))
    assert igraph.action_is_authorized(bob, Action(name="Share", resource_type="Document", resource="MyDoc"))
