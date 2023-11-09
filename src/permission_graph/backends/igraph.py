from typing import Any

import igraph

from permission_graph.backends.base import PermissionGraphBackend
from permission_graph.structs import (
    Action,
    Actor,
    EdgeType,
    Group,
    Resource,
    ResourceType,
    Vertex,
)


class IGraphMemoryBackend(PermissionGraphBackend):
    """IGraph based PermissionGraphBackend implementation."""

    def __init__(self):
        self._g = igraph.Graph(directed=True)

    def add_vertex(self, vertex: Vertex, **kwargs) -> None:
        try:
            self._get_igraph_vertex(vertex.id)
        except ValueError:
            self._g.add_vertex(f"{vertex.id}", vtype=vertex.vtype, **kwargs)
        else:
            raise ValueError(f"Vertex already exists: {vertex}")

    def remove_vertex(self, vertex: Vertex) -> None:
        v = self._g.vs.find(vertex.id)
        self._g.delete_vertices(v.index)

    def update_vertex_attributes(self, vertex: Vertex, **kwargs: Any) -> None:
        v = self._g.vs.find(vertex.id)
        for key, value in kwargs.items():
            v[key] = value

    def get_vertices_to(self, vertex: Vertex) -> list[Vertex]:
        v = self._get_igraph_vertex(vertex.id)
        sources = [self.vertex_factory(edge.source_vertex["name"]) for edge in self._g.es.select(_target=v)]
        return sources

    def get_vertices_from(self, vertex: Vertex) -> list[Vertex]:
        v = self._get_igraph_vertex(vertex.id)
        sources = [self.vertex_factory(edge.target_vertex["name"]) for edge in self._g.es.select(_source=v)]
        return sources

    def _get_igraph_vertex(self, vertex_id: str) -> igraph.Vertex:
        """Get an igraph vertex given a vertex id."""
        return self._g.vs.find(vertex_id)

    def vertex_exists(self, vertex: Vertex) -> bool:
        """Return True if a vertex wit hthat id already exists."""
        try:
            self._get_igraph_vertex(vertex.id)
            return True
        except ValueError:
            return False

    def add_edge(self, etype: EdgeType, source: Vertex, target: Vertex, **kwargs) -> None:
        v1 = self._get_igraph_vertex(source.id)
        v2 = self._get_igraph_vertex(target.id)
        try:
            self._get_igraph_edge(source, target)
        except ValueError:
            extra_attrs = {attr: [val] for attr, val in kwargs.items()}
            self._g.add_edges([(v1, v2)], attributes=dict(etype=[etype.value], **extra_attrs))
        else:
            raise ValueError(f"There is already an edge between vertices '{v1.index}' and '{v2.index}'")

    def _get_igraph_edge(self, source: Vertex, target: Vertex) -> igraph.Edge:
        """Return an IGraph edge given edge definition."""
        v1 = self._get_igraph_vertex(source.id)
        v2 = self._get_igraph_vertex(target.id)
        return self._g.es.find(_source=v1.index, _target=v2.index)

    def edge_exists(self, source: Vertex, target: Vertex) -> bool:
        """Return True if there is an edge between source and target."""
        try:
            self._get_igraph_edge(source, target)
            return True
        except ValueError:
            return False

    def remove_edge(self, source: Vertex, target: Vertex) -> None:
        """Remove an edge from the permission graph."""
        e = self._get_igraph_edge(source, target)
        if e is not None:
            self._g.delete_edges(e.index)

    def shortest_paths(self, source: Vertex, target: Vertex) -> list[list[Vertex]]:
        """Return all shortest paths from source to target."""
        v1 = self._get_igraph_vertex(source.id)
        v2 = self._get_igraph_vertex(target.id)
        paths = self._g.get_all_shortest_paths(v1, v2)
        output = []
        for path in paths:
            vertex_path = []
            for index in path:
                v = self._g.vs[index]
                vertex_path.append(self.vertex_factory(v["name"]))
            output.append(vertex_path)
        return output

    def get_edge_type(self, source: Vertex, target: Vertex) -> EdgeType:
        """Get the type of edge from source to target."""
        e = self._get_igraph_edge(source, target)
        if e is None:
            raise ValueError(f"There is no edge from {source} to {target}.")
        return EdgeType(e["etype"])

    def vertex_factory(self, vertex_id) -> Vertex:
        """Return a vertex from a vertex id."""
        v = self._get_igraph_vertex(vertex_id)
        attributes = v.attributes()
        attributes = {k: v for k, v in v.attributes().items() if k not in ("vtype", "name") and v is not None}
        return Vertex.factory(vertex_id, **attributes)
