from unittest.mock import MagicMock

import pytest

from permission_graph import (Action, EdgeType, Group, PermissionGraph,
                              Resource, ResourceType, User)


@pytest.fixture
def mock_backend():
    return MagicMock()


@pytest.fixture
def graph(mock_backend):
    g = PermissionGraph(backend=mock_backend)
    return g


@pytest.mark.unit
def test_add_user(graph):
    graph.backend.vertex_exists.side_effect = [False, True]
    user = User("Alice")
    graph.add_user(user)
    assert graph.backend.add_vertex.called_once_with(vertex=user)


@pytest.mark.unit
def test_remove_user(graph):
    user = User("Alice")
    graph.remove_user(user)
    assert graph.backend.remove_vertex.called_once_with(vertex=user)


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
def test_add_user_to_group(graph):
    alice = User("Alice")
    group = Group("Admins")
    graph.add_user_to_group(alice, group)
    graph.backend.add_edge.assert_called_once_with(EdgeType.MEMBER_OF, source=alice, target=group)


@pytest.mark.unit
def test_remove_user_from_group(graph):
    alice = User("Alice")
    admins = Group("Admins")
    graph.remove_user_from_group(alice, admins)


@pytest.mark.unit
def test_allow(graph):
    alice = User("Alice")
    foo = Resource("foo", ResourceType("Foo", ["bar"]))
    bar = Action("bar", foo)
    graph.allow(alice, bar)
    graph.backend.add_edge.assert_called_once_with(EdgeType.ALLOW, source=alice, target=bar)


@pytest.mark.unit
def test_deny(graph):
    alice = User("Alice")
    foo = Resource("foo", ResourceType("Foo", ["bar"]))
    bar = Action("bar", foo)
    graph.deny(alice, bar)
    graph.backend.add_edge.assert_called_once_with(EdgeType.DENY, source=alice, target=bar)


@pytest.mark.unit
def test_revoke(graph):
    alice = User("Alice")
    foo = Resource("foo", ResourceType("Foo", ["bar"]))
    bar = Action("bar", foo)
    graph.revoke(alice, bar)
    graph.backend.remove_edge.assert_called_once_with(alice, bar)
