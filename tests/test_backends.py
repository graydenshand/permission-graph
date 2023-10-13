import pytest

from permission_graph import EdgeType, Group, Resource, ResourceType, User
from permission_graph.backends import (IGraphMemoryBackend,
                                       PermissionGraphBackend)


@pytest.mark.integration
@pytest.mark.parametrize("backend", [IGraphMemoryBackend()])
def test_backend(backend: PermissionGraphBackend):
    """A simple test that any valid backend should pass."""

    # Add a vertex to the graph
    user = User("Alice")
    backend.add_vertex(user)
    assert backend.vertex_exists(user)

    # Vertexes are unique
    with pytest.raises(ValueError):
        backend.add_vertex(user)

    # Add a second vertex and an edge between it and the first
    group = Group("Admins")
    backend.add_vertex(group)
    with pytest.raises(ValueError):
        backend.get_edge_type(user, group)

    backend.add_edge(EdgeType.MEMBER_OF, user, group)
    assert backend.edge_exists(user, group)
    assert backend.get_vertices_to(group) == [user]
    assert backend.get_edge_type(user, group) == EdgeType.MEMBER_OF

    # Edges are unique
    with pytest.raises(ValueError):
        backend.add_edge(EdgeType.MEMBER_OF, user, group)

    # Add third vertex and two edges
    resource = Resource("foo", ResourceType("Foo", ["bar"]))
    backend.add_vertex(resource)
    backend.add_edge(EdgeType.DENY, group, resource)
    backend.add_edge(EdgeType.ALLOW, user, resource)

    assert backend.shortest_path(user, resource) == [user, resource]

    # Remove an edge
    backend.remove_edge(user, group)
    assert not backend.edge_exists(user, group)

    # Remove a vertex
    backend.remove_vertex(user)
    assert not backend.vertex_exists(user)
