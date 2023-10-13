import pytest

from permission_graph import Group, IGraphMemoryBackend, PermissionGraph, User


@pytest.fixture
def graph():
    g = PermissionGraph(backend=IGraphMemoryBackend())
    g.add_user(User("Alice"))
    return g


@pytest.fixture
def empty_graph():
    g = PermissionGraph(backend=IGraphMemoryBackend())
    return g


def test_igraph_test_vertex_exists(graph):
    assert graph.backend.vertex_exists(User("Alice"))
    assert not graph.backend.vertex_exists(User("Zenu"))


def test_igraph_remove_vertex(graph):
    user = User("Alice")
    graph.remove_user(user)
    assert not graph.backend.vertex_exists(user)


def test_igraph_add_member_to_group(graph):
    alice = User("Alice")
    admins = Group("Admins")
    graph.add_group(admins)
    graph.add_user_to_group(alice, admins)
    e = graph.backend._get_edge(alice, admins)
    assert e is not None
    assert e["etype"] == "MEMBER_OF"
