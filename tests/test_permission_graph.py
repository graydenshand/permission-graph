from unittest.mock import MagicMock

import pytest

from permission_graph import PermissionGraph
from permission_graph.structs import EdgeType, TieBreakerPolicy
from tests import ADMINS, ALICE, DOCUMENT, DOCUMENT_TYPE, VIEW_DOCUMENT


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
    graph.add_actor(ALICE)
    assert graph.backend.add_vertex.called_once_with(vertex=ALICE)


@pytest.mark.unit
def test_remove_actor(graph):
    graph.remove_actor(ALICE)
    assert graph.backend.remove_vertex.called_once_with(vertex=ALICE)


@pytest.mark.unit
def test_add_resource(graph):
    graph.add_resource(DOCUMENT)
    graph.backend.add_vertex.called_once_with(vertex=DOCUMENT)
    graph.backend.add_vertex.called_once_with(vertex=VIEW_DOCUMENT)
    graph.backend.add_edge.called_once_with(EdgeType.MEMBER_OF, VIEW_DOCUMENT, DOCUMENT)


@pytest.mark.unit
def test_remove_resource(graph):
    graph.remove_resource(DOCUMENT)
    assert graph.backend.remove_vertex.called_once_with(vertex=DOCUMENT)


@pytest.mark.unit
def test_add_group(graph):
    graph.backend.vertex_exists.side_effect = [False, True]
    graph.add_group(ADMINS)
    assert graph.backend.add_vertex.called_once_with(vertex=ADMINS)


@pytest.mark.unit
def test_remove_group(graph):
    graph.remove_group(ADMINS)
    assert graph.backend.remove_vertex.called_once_with(vertex=ADMINS)


@pytest.mark.unit
def test_add_actor_to_group(graph):
    graph.add_actor_to_group(ALICE, ADMINS)
    graph.backend.add_edge.assert_called_once_with(EdgeType.MEMBER_OF, source=ALICE, target=ADMINS)


@pytest.mark.unit
def test_remove_actor_from_group(graph):
    graph.remove_actor_from_group(ALICE, ADMINS)
    graph.backend.remove_edge.assert_called_once_with(source=ALICE, target=ADMINS)


@pytest.mark.unit
def test_allow(graph):
    graph.allow(ALICE, VIEW_DOCUMENT)
    graph.backend.add_edge.assert_called_once_with(EdgeType.ALLOW, source=ALICE, target=VIEW_DOCUMENT)


@pytest.mark.unit
def test_deny(graph):
    graph.deny(ALICE, VIEW_DOCUMENT)
    graph.backend.add_edge.assert_called_once_with(EdgeType.DENY, source=ALICE, target=VIEW_DOCUMENT)


@pytest.mark.unit
def test_revoke(graph):
    graph.revoke(ALICE, VIEW_DOCUMENT)
    graph.backend.remove_edge.assert_called_once_with(ALICE, VIEW_DOCUMENT)


@pytest.mark.unit
@pytest.mark.parametrize(
    "shortest_paths,terminal_edge_types,tie_breaker_policy,expected",
    [
        # No paths connecting agent to action - DENY
        ([], [EdgeType.ALLOW], TieBreakerPolicy.ANY_ALLOW, False),
        # One path that allows access - ALLOW
        ([[ALICE, VIEW_DOCUMENT]], [EdgeType.ALLOW], TieBreakerPolicy.ANY_ALLOW, True),
        # One path that denies access - DENY
        ([[ALICE, VIEW_DOCUMENT]], [EdgeType.DENY], TieBreakerPolicy.ANY_ALLOW, False),
        # Two paths, one allows one denies, tiebreaker policy ANY_ALLOW -- ALLOW
        (
            [
                [ALICE, VIEW_DOCUMENT],
                [ALICE, VIEW_DOCUMENT],
            ],
            [EdgeType.ALLOW, EdgeType.DENY],
            TieBreakerPolicy.ANY_ALLOW,
            True,
        ),
        # Two paths, one allows one denies, tiebreaker policy ALL_ALLOW -- DENY
        (
            [
                [ALICE, VIEW_DOCUMENT],
                [ALICE, VIEW_DOCUMENT],
            ],
            [EdgeType.ALLOW, EdgeType.DENY],
            TieBreakerPolicy.ALL_ALLOW,
            False,
        ),
        # Two paths, both deny, tiebreaker policy ANY_ALLOW -- DENY
        (
            [
                [ALICE, VIEW_DOCUMENT],
                [ALICE, VIEW_DOCUMENT],
            ],
            [EdgeType.DENY, EdgeType.DENY],
            TieBreakerPolicy.ANY_ALLOW,
            False,
        ),
    ],
)
def test_action_is_authorized(mock_backend, shortest_paths, terminal_edge_types, tie_breaker_policy, expected):
    graph = PermissionGraph(backend=mock_backend, tie_breaker_policy=tie_breaker_policy)
    graph.backend.shortest_paths.return_value = shortest_paths
    graph.backend.get_edge_type.side_effect = terminal_edge_types
    assert graph.action_is_authorized(ALICE, VIEW_DOCUMENT) is expected


@pytest.mark.unit
def test_terminal_paths(graph):
    graph.backend.get_vertices_from.side_effect = [
        [ADMINS, VIEW_DOCUMENT],  # ALICE -> ADMINS, ALICE -> VIEW_DOCUMENT
        [],  # ADMINS -X
        [DOCUMENT],  # VIEW_DOCUMENT -> DOCUMENT
        [DOCUMENT_TYPE],  # DOCUMENT -> DOCUMENT_TYPE
    ]
