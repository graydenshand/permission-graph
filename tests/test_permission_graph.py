from unittest.mock import MagicMock

import pytest

from permission_graph import PermissionGraph
from permission_graph.structs import (Action, Actor, EdgeType, Group, Resource,
                                      ResourceType)


@pytest.fixture
def mock_backend():
    return MagicMock()


@pytest.fixture
def graph(mock_backend):
    g = PermissionGraph(backend=mock_backend)
    return g


@pytest.mark.unit
def test_add_actor(graph):
    graph.backend.vertex_exists.side_effect = [False, True]
    actor = Actor("Alice")
    graph.add_actor(actor)
    assert graph.backend.add_vertex.called_once_with(vertex=actor)


@pytest.mark.unit
def test_remove_actor(graph):
    actor = Actor("Alice")
    graph.remove_actor(actor)
    assert graph.backend.remove_vertex.called_once_with(vertex=actor)


@pytest.mark.unit
def test_add_resource(graph):
    resource_type = ResourceType("Foo", actions=["bar"])
    resource = Resource("foo", resource_type)
    # Verify ValueError raised when specifying unregistered ResourceType
    with pytest.raises(ValueError):
        graph.add_resource(resource)
    graph.register_resource_type(resource_type)
    graph.add_resource(resource)
    assert graph.backend.add_vertex.called_once_with(vertex=resource)
    assert graph.backend.add_vertex.called_once_with(vertex=resource)


@pytest.mark.unit
def test_remove_resource(graph):
    resource = Resource("foo", ResourceType("Foo", actions=["bar"]))
    graph.remove_resource(resource)
    assert graph.backend.remove_vertex.called_once_with(vertex=resource)


@pytest.mark.unit
def test_add_group(graph):
    graph.backend.vertex_exists.side_effect = [False, True]
    group = Group("Admins")
    graph.add_group(group)
    assert graph.backend.add_vertex.called_once_with(vertex=group)


@pytest.mark.unit
def test_remove_group(graph):
    group = Group("Admins")
    graph.remove_group(group)
    assert graph.backend.remove_vertex.called_once_with(vertex=group)


@pytest.mark.unit
def test_add_actor_to_group(graph):
    alice = Actor("Alice")
    group = Group("Admins")
    graph.add_actor_to_group(alice, group)
    graph.backend.add_edge.assert_called_once_with(EdgeType.MEMBER_OF, source=alice, target=group)


@pytest.mark.unit
def test_remove_actor_from_group(graph):
    alice = Actor("Alice")
    admins = Group("Admins")
    graph.remove_actor_from_group(alice, admins)


@pytest.mark.unit
def test_allow(graph):
    alice = Actor("Alice")
    foo = Resource("foo", ResourceType("Foo", ["bar"]))
    bar = Action("bar", foo)
    graph.allow(alice, bar)
    graph.backend.add_edge.assert_called_once_with(EdgeType.ALLOW, source=alice, target=bar)


@pytest.mark.unit
def test_deny(graph):
    alice = Actor("Alice")
    foo = Resource("foo", ResourceType("Foo", ["bar"]))
    bar = Action("bar", foo)
    graph.deny(alice, bar)
    graph.backend.add_edge.assert_called_once_with(EdgeType.DENY, source=alice, target=bar)


@pytest.mark.unit
def test_revoke(graph):
    alice = Actor("Alice")
    foo = Resource("foo", ResourceType("Foo", ["bar"]))
    bar = Action("bar", foo)
    graph.revoke(alice, bar)
    graph.backend.remove_edge.assert_called_once_with(alice, bar)
