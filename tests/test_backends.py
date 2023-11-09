import uuid

import psycopg2
import pytest

from permission_graph.backends.base import PermissionGraphBackend
from permission_graph.backends.igraph import IGraphMemoryBackend
from permission_graph.backends.postgres import PostgresBackend
from permission_graph.structs import Actor, EdgeType, Vertex
from tests import ADMINS, ALICE, DOCUMENT, DOCUMENT_TYPE, VIEW_DOCUMENT


@pytest.fixture(
    params=[
        pytest.param((IGraphMemoryBackend, ()), id="igraph"),
        pytest.param((PostgresBackend, (f"postgresql:///{uuid.uuid4().hex}",)), id="postgres"),
    ]
)
def backend(request):
    backend_class, init_args = request.param
    b = backend_class(*init_args)

    # Create new pg database
    if backend_class == PostgresBackend:
        db_name = init_args[0].split("/")[-1]
        conn = psycopg2.connect("postgresql:///")
        try:
            conn.autocommit = True
            with conn.cursor() as cursor:
                cursor.execute(f'CREATE DATABASE "{db_name}"')
        finally:
            conn.close()
        b.init_db()

    # yield to test
    yield b

    # Destroy pg database
    if backend_class == PostgresBackend:
        db_name = init_args[0].split("/")[-1]
        conn = psycopg2.connect("postgresql:///")
        try:
            conn.autocommit = True
            with conn.cursor() as cursor:
                cursor.execute(f'DROP DATABASE "{db_name}"')
        finally:
            conn.close()


@pytest.fixture
def base_vertices(
    backend: PermissionGraphBackend,
) -> tuple[Vertex]:
    """Add some vertices to the graph."""
    backend.add_vertex(ALICE)
    backend.add_vertex(ADMINS)
    backend.add_vertex(DOCUMENT_TYPE, actions=DOCUMENT_TYPE.actions)
    backend.add_vertex(DOCUMENT)
    backend.add_vertex(VIEW_DOCUMENT)
    return ALICE, ADMINS, DOCUMENT_TYPE, DOCUMENT, VIEW_DOCUMENT


@pytest.fixture
def base_edges(
    backend: PermissionGraphBackend,
    base_vertices: tuple[Vertex],
) -> None:
    """Add some edges to the graph."""
    backend.add_edge(EdgeType.MEMBER_OF, ALICE, ADMINS)
    backend.add_edge(EdgeType.MEMBER_OF, DOCUMENT, DOCUMENT_TYPE)
    backend.add_edge(EdgeType.MEMBER_OF, VIEW_DOCUMENT, DOCUMENT)
    backend.add_edge(EdgeType.ALLOW, ADMINS, VIEW_DOCUMENT)


def test_prevents_duplicate_vertices(backend: PermissionGraphBackend, base_vertices: tuple[Vertex]) -> None:
    with pytest.raises(ValueError):
        backend.add_vertex(ALICE)


def test_vertex_exists(backend: PermissionGraphBackend, base_vertices: tuple[Vertex]) -> None:
    assert backend.vertex_exists(ALICE)
    bob = Actor(name="bob")
    assert not backend.vertex_exists(bob)


def test_no_edge_found_raises_value_error(backend: PermissionGraphBackend, base_vertices: tuple[Vertex]) -> None:
    with pytest.raises(ValueError):
        backend.get_edge_type(ALICE, ADMINS)


def test_get_edge_type(backend: PermissionGraphBackend, base_edges: None) -> None:
    assert backend.get_edge_type(ALICE, ADMINS) == EdgeType.MEMBER_OF


def test_edge_exists(backend: PermissionGraphBackend, base_edges: None) -> None:
    assert backend.edge_exists(ALICE, ADMINS)
    assert not backend.edge_exists(ALICE, DOCUMENT)


def test_get_vertices_to(backend: PermissionGraphBackend, base_edges: None) -> None:
    assert backend.get_vertices_to(ADMINS) == [ALICE]


def test_get_vertices_from(backend: PermissionGraphBackend, base_edges: None) -> None:
    assert backend.get_vertices_to(VIEW_DOCUMENT) == [ADMINS]


def test_prevents_duplicate_and_conflicting_edges(backend: PermissionGraphBackend, base_edges: None) -> None:
    with pytest.raises(ValueError):
        backend.add_edge(EdgeType.MEMBER_OF, ALICE, ADMINS)


def test_shortest_path(backend: PermissionGraphBackend, base_edges: None) -> None:
    assert backend.shortest_paths(ALICE, VIEW_DOCUMENT) == [[ALICE, ADMINS, VIEW_DOCUMENT]]
    backend.add_edge(EdgeType.DENY, ALICE, VIEW_DOCUMENT)
    assert backend.shortest_paths(ALICE, VIEW_DOCUMENT) == [[ALICE, VIEW_DOCUMENT]]


def test_remove_edge(backend: PermissionGraphBackend, base_edges: None) -> None:
    assert backend.edge_exists(ADMINS, VIEW_DOCUMENT)
    backend.remove_edge(ADMINS, VIEW_DOCUMENT)
    assert not backend.edge_exists(ADMINS, VIEW_DOCUMENT)


def test_vertex_factory(backend: PermissionGraphBackend, base_vertices: tuple[Vertex]):
    for vertex in base_vertices:
        assert backend.vertex_factory(vertex.id) == vertex


def test_remove_vertex(backend: PermissionGraphBackend, base_vertices: tuple[Vertex]):
    assert backend.vertex_exists(ALICE)
    backend.remove_vertex(ALICE)
    assert not backend.vertex_exists(ALICE)


def test_update_vertex_attributes(backend: PermissionGraphBackend, base_vertices: tuple[Vertex]) -> None:
    backend.update_vertex_attributes(ALICE, foo="bar")
    # new attribute causes ValueError in vertex factory
    with pytest.raises(TypeError) as e:
        assert backend.vertex_factory(ALICE.id)
        assert e == "Vertex.from_id() got an unexpected keyword argument 'foo'"
