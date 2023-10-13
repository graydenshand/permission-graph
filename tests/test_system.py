"""System level tests."""
import pytest

from permission_graph import (Action, EdgeType, Group, IGraphMemoryBackend,
                              PermissionGraph, Resource, ResourceType,
                              TieBreakerPolicy, User)


@pytest.fixture
def igraph():
    backend = IGraphMemoryBackend()
    graph = PermissionGraph(backend=backend, tie_breaker_policy=TieBreakerPolicy.ANY_ALLOW)
    return graph


@pytest.mark.integration
def test_system(igraph):
    alice = User("Alice")
    igraph.add_user(alice)

    admins = Group("Admins")
    igraph.add_group(admins)

    igraph.add_user_to_group(alice, admins)

    document_type = ResourceType("Document", ["View", "Edit", "Share"])
    igraph.register_resource_type(document_type)

    document = Resource("MyDoc", document_type)
    igraph.add_resource(document)

    view_document = Action("View", document)
    assert not igraph.action_is_authorized(alice, view_document)

    igraph.allow(admins, view_document)
    assert igraph.action_is_authorized(alice, view_document)

    igraph.deny(alice, view_document)
    assert not igraph.action_is_authorized(alice, view_document)

    igraph.revoke(alice, view_document)
    assert igraph.action_is_authorized(alice, view_document)

    # Conflicting dependencies
    public = Group("Public")
    igraph.add_group(public)
    igraph.add_user_to_group(alice, public)
    igraph.deny(public, view_document)
    assert igraph.action_is_authorized(alice, view_document)

    # Permission propagation
    directory_type = ResourceType("Document", ["View", "Create", "Share"])
    igraph.register_resource_type(directory_type)
    directory = Resource("Home", directory_type)
    igraph.add_resource(directory)

    bob = User("Bob")
    igraph.add_user(bob)
    assert not igraph.action_is_authorized(bob, Action("Share", document))

    igraph.allow(Action("Share", directory), Action("Share", document))
    igraph.allow(bob, Action("Share", directory))
    assert igraph.action_is_authorized(bob, Action("Share", document))
