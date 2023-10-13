import pytest

from permission_graph import EdgeType, Group, User
from permission_graph.backends import (IGraphMemoryBackend,
                                       PermissionGraphBackend)


@pytest.mark.integration
@pytest.mark.parametrize("backend", [IGraphMemoryBackend()])
def test_backend(backend: PermissionGraphBackend):
    """Test that all backends work as expected."""
    user = User("Alice")
    backend.add_vertex(user)
    assert backend.vertex_exists(user)

    group = Group("Admins")
    backend.add_vertex(group)
    backend.add_edge(EdgeType.MEMBER_OF, user, group)
    assert backend.edge_exists(user, group)

    backend.remove_edge(user, group)
    assert not backend.edge_exists(user, group)

    backend.remove_vertex(user)
    assert not backend.vertex_exists(user)
