import abc
from typing import Any

from permission_graph.structs import EdgeType, ResourceType, Vertex


class PermissionGraphBackend(abc.ABC):
    """Base class for PermissionGraph interface."""

    @abc.abstractmethod
    def add_vertex(self, vertex: Vertex, **kwargs) -> None:
        """Add a vertex to the permission graph.

        Raises ValueError if vertex already exists.
        """

    @abc.abstractmethod
    def remove_vertex(self, vertex: Vertex, **kwargs) -> None:
        """Remove a vertex from the permission graph."""

    @abc.abstractmethod
    def vertex_exists(self, vertex: Vertex) -> bool:
        """Check if a vertex with vtype=vtype and id=id already exists."""

    @abc.abstractmethod
    def get_vertices_to(self, vertex: Vertex) -> list[Vertex]:
        """Get all vertices that target a vertex."""

    @abc.abstractmethod
    def get_vertices_from(self, vertex: Vertex) -> list[Vertex]:
        """Get all vertices that a vertex targets."""

    @abc.abstractmethod
    def update_vertex_attributes(self, vertex: Vertex, **kwargs):
        """Update one or more attributes of a vertex."""

    @abc.abstractmethod
    def add_edge(self, etype: str, source: Vertex, target: Vertex, **kwargs: Any) -> None:
        """Add a edge to the permission graph.

        Args:
            etype: edge type (one of 'member_of', 'allow', 'deny')
            source: source vertex
            target: target vertex
            **kwargs: addition attributes to add to edge

        Raises ValueError if an edge from source to target already exists.
        """

    @abc.abstractmethod
    def edge_exists(self, source: Vertex, target: Vertex) -> bool:
        """Return True if edge exists."""

    @abc.abstractmethod
    def remove_edge(self, source: Vertex, target: Vertex) -> None:
        """Remove an edge from the permission graph."""

    @abc.abstractmethod
    def shortest_paths(self, source: Vertex, target: Vertex) -> list[list[Vertex]]:
        """Return the lists of vertices that make the shortest paths from source to target.

        Returns:
            - If there is a true shortest path (no ties), return a list containing one element
                (the shortest path).
            - Otherwise, return a list containing all of the paths with length equal to the
                shortest path.
        """

    @abc.abstractmethod
    def get_edge_type(self, source: Vertex, target: Vertex) -> EdgeType:
        """Return the EdgeType of the edge connecting two vertices.

        Raises ValueError if there is no edge between the two vertices.
        """

    @abc.abstractmethod
    def vertex_factory(self, vertex_id) -> Vertex:
        """Return a vertex from a vertex id.

        Given a vertex id, return an vertex object of the appropriate subclass.
        """
