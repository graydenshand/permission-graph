from unittest.mock import MagicMock

import pytest

from permission_graph import (EdgeType, Group, PermissionGraph, Resource,
                              ResourceType, User)


@pytest.fixture
def mock_backend():
    return MagicMock()


@pytest.fixture
def graph(mock_backend):
    g = PermissionGraph(backend=mock_backend)
    return g


@pytest.fixture
def empty_graph(mock_backend):
    g = PermissionGraph(backend=mock_backend)
    return g


@pytest.mark.parametrize(
    "vertex_exists,resource_type,expected",
    [
        (True, ResourceType(name="foo", actions=["create_foo"]), ValueError),
        (False, None, ValueError),
        (False, ResourceType(name="foo", actions=["create_foo"]), None),
    ],
)
def test_validate_vertex(graph, vertex_exists, resource_type, expected):
    graph.backend.vertex_exists.return_value = vertex_exists
    resource = Resource("Foo", resource_type=resource_type)
    if expected is not None:
        with pytest.raises(expected):
            graph.validate_vertex(resource)
    else:
        assert graph.validate_vertex(resource) is None


def test_add_user(graph):
    graph.backend.vertex_exists.side_effect = [False, True]
    graph.validate_vertex = MagicMock()
    user = User("Alice")
    graph.add_user(user)
    assert graph.validate_vertex.called_once_with(vertex=user)
    assert graph.backend.add_vertex.called_once_with(vertex=user)


def test_remove_user(graph):
    user = User("Alice")
    graph.remove_user(user)
    assert graph.backend.remove_vertex.called_once_with(vertex=user)


def test_add_resource(graph):
    resource = Resource("foo", ResourceType("Foo", actions=["bar"]))
    graph.validate_vertex = MagicMock()
    graph.add_resource(resource)
    assert graph.backend.add_vertex.called_once_with(vertex=resource)
    assert graph.resource_types == [resource.resource_type]
    assert graph.backend.add_vertex.called_once_with(vertex=resource)


def test_remove_resource(graph):
    resource = Resource("foo", ResourceType("Foo", actions=["bar"]))
    graph.remove_resource(resource)
    assert graph.backend.remove_vertex.called_once_with(vertex=resource)


def test_add_group(graph):
    graph.backend.vertex_exists.side_effect = [False, True]
    graph.validate_vertex = MagicMock()
    group = Group("Admins")
    graph.add_group(group)
    assert graph.validate_vertex.called_once_with(vertex=group)
    assert graph.backend.add_vertex.called_once_with(vertex=group)


def test_remove_group(graph):
    group = Group("Admins")
    graph.remove_group(group)
    assert graph.backend.remove_vertex.called_once_with(vertex=group)


@pytest.mark.parametrize(
    "edge_exists,etype,source,target,action,expected",
    [
        (False, EdgeType.MEMBER_OF, Group("Admins"), Group("SuperAdmins"), None, ValueError),
        (False, EdgeType.ALLOW, Resource("Foo", ResourceType("Foo", ["bar"])), User("Alice"), "bar", ValueError),
        (False, EdgeType.DENY, Resource("Foo", ResourceType("Foo", ["bar"])), User("Alice"), "bar", ValueError),
        (False, EdgeType.DENY, Group("Admins"), User("Alice"), "bar", ValueError),
        (True, EdgeType.ALLOW, Group("Admins"), Resource("Foo", ResourceType("Foo", ["bar"])), "bar", ValueError),
        (False, EdgeType.DENY, User("Alice"), Resource("Foo", ResourceType("Foo", ["bar"])), "foo", ValueError),
        (False, EdgeType.DENY, User("Alice"), Resource("Foo", ResourceType("Foo", ["bar"])), "bar", None),
        (False, EdgeType.ALLOW, Group("Admins"), Resource("Foo", ResourceType("Foo", ["bar"])), "bar", None),
        (False, EdgeType.MEMBER_OF, User("Alice"), Group("Admins"), None, None),
    ],
)
def test_validate_edge(graph, edge_exists, etype, source, target, action, expected):
    graph.backend.edge_exists.return_value = edge_exists
    if expected is not None:
        with pytest.raises(expected):
            graph.validate_edge(etype, source, target, action)
    else:
        assert graph.validate_edge(etype, source, target, action) is None


def test_add_user_to_group(graph):
    graph.validate_edge = MagicMock()
    alice = User("Alice")
    group = Group("Admins")
    graph.add_user_to_group(alice, group)
    graph.validate_edge.assert_called_once_with(EdgeType.MEMBER_OF, source=alice, target=group)
    graph.backend.add_edge.assert_called_once_with(EdgeType.MEMBER_OF, source=alice, target=group)


def test_remove_user_from_group(graph):
    graph.validate_edge = MagicMock()
    alice = User("Alice")
    admins = Group("Admins")
    graph.remove_user_from_group(alice, admins)


def test_allow(graph):
    graph.validate_edge = MagicMock()
    alice = User("Alice")
    foo = Resource("foo", ResourceType("Foo", ["bar"]))
    graph.allow(alice, foo, "bar")
    graph.validate_edge.assert_called_once_with(EdgeType.ALLOW, source=alice, target=foo, action="bar")
    graph.backend.add_edge.assert_called_once_with(EdgeType.ALLOW, source=alice, target=foo, action="bar")


def test_deny(graph):
    graph.validate_edge = MagicMock()
    alice = User("Alice")
    foo = Resource("foo", ResourceType("Foo", ["bar"]))
    graph.deny(alice, foo, "bar")
    graph.validate_edge.assert_called_once_with(EdgeType.DENY, source=alice, target=foo, action="bar")
    graph.backend.add_edge.assert_called_once_with(EdgeType.DENY, source=alice, target=foo, action="bar")


def test_revoke(graph):
    graph.validate_edge = MagicMock()
    alice = User("Alice")
    foo = Resource("foo", ResourceType("Foo", ["bar"]))
    graph.revoke(alice, foo, "bar")
    graph.backend.remove_edge.assert_called_once_with(alice, foo)
