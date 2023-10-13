import igraph

from permission_graph.backends.base import PermissionGraphBackend
from permission_graph.structs import EdgeType, Vertex, vertex_factory


class IGraphMemoryBackend(PermissionGraphBackend):
    """IGraph based PermissionGraphBackend implementation."""

    def __init__(self):
        self.g = igraph.Graph(directed=True)

    def add_vertex(self, vertex: Vertex, **kwargs) -> None:
        if self._get_vertex(vertex) is not None:
            raise ValueError(f"Vertex already exists: {vertex}")

        self.g.add_vertices(f"{vertex.vertex_id}", attributes=dict(vtype=vertex.vtype, **kwargs))

    def remove_vertex(self, vertex: Vertex) -> None:
        v = self._get_vertex(vertex)
        if v is not None:
            self.g.delete_vertices(v.index)

    def get_vertices_to(self, vertex: Vertex) -> list[Vertex]:
        v = self._get_vertex(vertex)
        sources = [edge.source_vertex for edge in self.g.es.select(_target=v)]
        return [vertex_factory(source["vtype"], source["name"]) for source in sources]

    def _get_vertex(self, vertex: Vertex) -> igraph.Vertex:
        try:
            return self.g.vs.find(name_eq=vertex.vertex_id)
        except (KeyError, ValueError):
            return None

    def vertex_exists(self, vertex: Vertex) -> bool:
        v = self._get_vertex(vertex)
        return v is not None

    def add_edge(self, etype: EdgeType, source: Vertex, target: Vertex, **kwargs) -> None:
        v1 = self._get_vertex(source)
        v2 = self._get_vertex(target)
        if self._get_edge(source, target) is None:
            extra_attrs = {attr: [val] for attr, val in kwargs.items()}
            self.g.add_edges([(v1, v2)], attributes=dict(etype=[etype.value], **extra_attrs))
        else:
            raise ValueError(f"There is already an edge between vertices '{v1.index}' and '{v2.index}'")

    def _get_edge(self, source: Vertex, target: Vertex) -> igraph.Edge:
        """Return an IGraph edge given edge definition."""
        v1 = self._get_vertex(source)
        v2 = self._get_vertex(target)
        try:
            return self.g.es.find(_source=v1.index, _target=v2.index)
        except ValueError:
            return None

    def edge_exists(self, source: Vertex, target: Vertex) -> bool:
        return self._get_edge(source, target) is not None

    def remove_edge(self, source: Vertex, target: Vertex) -> None:
        e = self._get_edge(source, target)
        if e is not None:
            self.g.delete_edges(e.index)

    def shortest_paths(self, source: Vertex, target: Vertex) -> list[list[Vertex]]:
        v1 = self._get_vertex(source)
        v2 = self._get_vertex(target)
        paths = self.g.get_all_shortest_paths(v1, v2)
        output = []
        for path in paths:
            vertex_path = []
            for index in path:
                v = self.g.vs[index]
                vertex_path.append(vertex_factory(v["vtype"], v["name"]))
            output.append(vertex_path)
        return output

    def get_edge_type(self, source: Vertex, target: Vertex) -> EdgeType:
        e = self._get_edge(source, target)
        if e is None:
            raise ValueError(f"There is no edge from {source} to {target}.")
        return EdgeType(e["etype"])
