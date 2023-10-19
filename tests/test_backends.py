import pytest

from permission_graph.backends.base import PermissionGraphBackend
from permission_graph.backends.igraph import IGraphMemoryBackend
from permission_graph.structs import (
    Action,
    Actor,
    EdgeType,
    Group,
    Resource,
    ResourceType,
    Vertex,
)


@pytest.fixture(params=[pytest.param(IGraphMemoryBackend, id="igraph")])
def backend(request):
    return request.param()


@pytest.fixture
def base_vertices(
    backend: PermissionGraphBackend,
    alice: Actor,
    admins: Group,
    document_type: ResourceType,
    document: Resource,
    view_document: Action,
) -> tuple[Vertex]:
    """Add some vertices to the graph."""
    backend.add_vertex(alice)
    backend.add_vertex(admins)
    backend.add_vertex(document_type, actions=document_type.actions)
    backend.add_vertex(document)
    backend.add_vertex(view_document)
    return alice, admins, document_type, document, view_document


@pytest.fixture
def base_edges(
    backend: PermissionGraphBackend,
    base_vertices: tuple[Vertex],
    alice: Actor,
    admins: Group,
    document_type: ResourceType,
    document: Resource,
    view_document: Action,
) -> None:
    """Add some edges to the graph."""
    backend.add_edge(EdgeType.MEMBER_OF, alice, admins)
    backend.add_edge(EdgeType.MEMBER_OF, document, document_type)
    backend.add_edge(EdgeType.MEMBER_OF, view_document, document)
    backend.add_edge(EdgeType.ALLOW, admins, view_document)


def test_prevents_duplicate_vertices(backend: PermissionGraphBackend, base_vertices: tuple[Vertex]) -> None:
    with pytest.raises(ValueError):
        backend.add_vertex(base_vertices[0])


def test_vertex_exists(backend: PermissionGraphBackend, base_vertices: tuple[Vertex]) -> None:
    assert backend.vertex_exists(base_vertices[0])
    bob = Actor(name="bob")
    assert not backend.vertex_exists(bob)


def test_no_edge_found_raises_value_error(
    backend: PermissionGraphBackend, base_vertices: tuple[Vertex], alice: Actor, admins: Group
) -> None:
    with pytest.raises(ValueError):
        backend.get_edge_type(alice, admins)


def test_get_edge_type(backend: PermissionGraphBackend, base_edges: None, alice: Actor, admins: Group) -> None:
    assert backend.get_edge_type(alice, admins) == EdgeType.MEMBER_OF


def test_edge_exists(
    backend: PermissionGraphBackend, base_edges: None, alice: Actor, admins: Group, document: Resource
) -> None:
    assert backend.edge_exists(alice, admins)
    assert not backend.edge_exists(alice, document)


def test_get_vertices_to(backend: PermissionGraphBackend, base_edges: None, alice: Actor, admins: Group) -> None:
    assert backend.get_vertices_to(admins) == [alice]


def test_get_vertices_from(
    backend: PermissionGraphBackend, base_edges: None, view_document: Action, admins: Group
) -> None:
    assert backend.get_vertices_to(view_document) == [admins]


def test_prevents_duplicate_and_conflicting_edges(
    backend: PermissionGraphBackend, base_edges: None, alice: Actor, admins: Group
) -> None:
    with pytest.raises(ValueError):
        backend.add_edge(EdgeType.MEMBER_OF, alice, admins)


def test_shortest_path(
    backend: PermissionGraphBackend, base_edges: None, alice: Actor, admins: Group, view_document: Action
) -> None:
    assert backend.shortest_paths(alice, view_document) == [[alice, admins, view_document]]
    backend.add_edge(EdgeType.DENY, alice, view_document)
    assert backend.shortest_paths(alice, view_document) == [[alice, view_document]]


def test_remove_edge(backend: PermissionGraphBackend, base_edges: None, view_document: Action, admins: Group) -> None:
    assert backend.edge_exists(admins, view_document)
    backend.remove_edge(admins, view_document)
    assert not backend.edge_exists(admins, view_document)


def test_vertex_factory(backend: PermissionGraphBackend, base_vertices: tuple[Vertex]):
    for vertex in base_vertices:
        assert backend.vertex_factory(vertex.id) == vertex


def test_remove_vertex(backend: PermissionGraphBackend, base_vertices: tuple[Vertex]):
    assert backend.vertex_exists(base_vertices[0])
    backend.remove_vertex(base_vertices[0])
    assert not backend.vertex_exists(base_vertices[0])


def test_update_vertex_attributes(backend: PermissionGraphBackend, base_vertices: tuple[Vertex]) -> None:
    backend.update_vertex_attributes(base_vertices[0], foo="bar")
    # new attribute causes ValueError in vertex factory
    with pytest.raises(TypeError) as e:
        assert backend.vertex_factory(base_vertices[0].id)
        assert e == "Vertex.from_id() got an unexpected keyword argument 'foo'"
