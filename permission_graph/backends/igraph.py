import igraph

from permission_graph.backends.base import PermissionGraphBackend
from permission_graph.structs import EdgeType, Vertex


class IGraphMemoryBackend(PermissionGraphBackend):
    """IGraph based PermissionGraphBackend implementation."""

    def __init__(self):
        self.g = igraph.Graph(directed=True)

    def add_vertex(self, vertex: Vertex, **kwargs) -> None:
        self.g.add_vertices(f"{vertex.vertex_id}", attributes=dict(vtype=vertex.vtype, **kwargs))

    def remove_vertex(self, vertex: Vertex) -> None:
        v = self.get_vertex(vertex)
        if v is not None:
            self.g.delete_vertices(v.index)

    def get_vertex(self, vertex: Vertex) -> igraph.Vertex:
        try:
            return self.g.vs.find(name_eq=f"{vertex.vertex_id}")
        except (KeyError, ValueError):
            return None

    def vertex_exists(self, vertex: Vertex) -> bool:
        v = self.get_vertex(vertex)
        return v is not None

    def add_edge(self, etype: EdgeType, source: Vertex, target: Vertex, **kwargs) -> None:
        v1 = self.get_vertex(source)
        v2 = self.get_vertex(target)
        if self.get_edge(source, target) is None:
            extra_attrs = {attr: [val] for attr, val in kwargs.items()}
            self.g.add_edges([(v1, v2)], attributes=dict(etype=[etype.value], **extra_attrs))
        else:
            raise ValueError(f"There is already an edge between vertices '{v1.index}' and '{v2.index}'")

    def get_edge(self, source: Vertex, target: Vertex) -> igraph.Edge:
        """Return an IGraph edge given edge definition."""
        v1 = self.get_vertex(source)
        v2 = self.get_vertex(target)
        try:
            return self.g.es.find(_source=v1.index, _target=v2.index)
        except ValueError:
            return None

    def remove_edge(self, source: Vertex, target: Vertex) -> None:
        v1 = self.get_vertex(source)
        v2 = self.get_vertex(target)
        e = self.get_edge(v1, v2)
        if e is not None:
            self.g.delete_edges(e.index)

    def action_is_authorized(self, user_id: str, resource_id: str, action: str) -> list[int]:
        """Return the shortest path for a given user, resource and action."""
        v1 = self.get_vertex("user", user_id)
        v2 = self.get_vertex("resource", resource_id)

        # Inefficient for a dense permissions graph with many paths connecting user and resource
        path_list = sorted(
            self.g.get_all_simple_paths(
                v1,
                v2,
            ),
            key=lambda path: len(path),
        )

        for path in path_list:
            # last path should be permission
            edge = self.g.es.find(_source=path[-2], _target=path[-1], action_eq=action)
            if edge is not None:
                return edge["etype"] == "allow"
        else:
            return []
