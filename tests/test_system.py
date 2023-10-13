"""System level tests."""
import pytest

from permission_graph import (Action, EdgeType, Group, IGraphMemoryBackend,
                              PermissionGraph, Resource, ResourceType, User)

ig_backend = IGraphMemoryBackend()
ig_graph = PermissionGraph(backend=ig_backend)


@pytest.mark.system
@pytest.mark.parametrize("graph", [ig_graph])
def test_system(graph):
    alice = User("Alice")
    graph.add_user(alice)

    admins = Group("Admins")
    graph.add_group(admins)

    graph.add_user_to_group(alice, admins)

    document_type = ResourceType("Document", ["View", "Edit", "Share"])
    graph.register_resource_type(document_type)

    document = Resource("MyDoc", document_type)
    graph.add_resource(document)

    view_document = Action("View", document)
    graph.deny(admins, view_document)
    assert not graph.action_is_authorized(alice, view_document)

    graph.allow(alice, view_document)
    assert graph.action_is_authorized(alice, view_document)
