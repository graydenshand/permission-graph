import pytest

from permission_graph.backends.base import PermissionGraphBackend
from permission_graph.backends.igraph import IGraphMemoryBackend
from permission_graph.structs import (Action, Actor, EdgeType, Group, Resource,
                                      ResourceType)


@pytest.mark.integration
@pytest.mark.parametrize("backend", [IGraphMemoryBackend()])
def test_backend(backend: PermissionGraphBackend):
    """A simple test that any valid backend should pass."""

    # Add a vertex to the graph
    actor = Actor("Alice")
    backend.add_vertex(actor)
    assert backend.vertex_exists(actor)

    # Vertexes are unique
    with pytest.raises(ValueError):
        backend.add_vertex(actor)

    # Add a second vertex and an edge between it and the first
    group = Group("Admins")
    backend.add_vertex(group)
    with pytest.raises(ValueError):
        backend.get_edge_type(actor, group)

    backend.add_edge(EdgeType.MEMBER_OF, actor, group)
    assert backend.edge_exists(actor, group)
    assert backend.get_vertices_to(group) == [actor]
    assert backend.get_edge_type(actor, group) == EdgeType.MEMBER_OF

    # Edges are unique
    with pytest.raises(ValueError):
        backend.add_edge(EdgeType.MEMBER_OF, actor, group)

    # Add more vertices and edges
    resource = Resource("foo", ResourceType("Foo", ["bar"]))
    action = Action("bar", resource)
    backend.add_vertex(action)
    backend.add_edge(EdgeType.DENY, group, action)
    backend.add_edge(EdgeType.ALLOW, actor, action)
    assert backend.shortest_paths(actor, action) == [[actor, action]]
    assert backend.get_edge_type(actor, action) == EdgeType.ALLOW

    # Remove an edge
    backend.remove_edge(actor, group)
    assert not backend.edge_exists(actor, group)

    # Remove a vertex
    backend.remove_vertex(actor)
    assert not backend.vertex_exists(actor)
