import abc

from permission_graph.structs import Resource, User, Vertex


class PermissionGraphBackend(abc.ABC):
    """Base class for PermissionGraph interface."""

    @abc.abstractmethod
    def add_vertex(self, vertex: Vertex, **kwargs) -> None:
        """Add a vertex to the permission graph."""

    @abc.abstractmethod
    def remove_vertex(self, vertex: Vertex, **kwargs) -> None:
        """Remove a vertex from the permission graph."""

    @abc.abstractmethod
    def vertex_exists(self, vertex: Vertex) -> bool:
        """Check if a vertex with vtype=vtype and id=id already exists."""

    @abc.abstractmethod
    def add_edge(self, etype: str, source: Vertex, target: Vertex, **kwargs) -> None:
        """Add a edge to the permission graph.

        Args:
            - etype: edge type (one of 'member_of', 'allow', 'deny')
            - source: source vertex
            - target: target vertex
            - **kwargs: addition attributes to add to edge
        """

    @abc.abstractmethod
    def edge_exists(self, source: Vertex, target: Vertex) -> bool:
        """Return True if edge exists."""

    @abc.abstractmethod
    def edge_exists(self, source: Vertex, target: Vertex) -> bool:
        """Return True if edge exists."""

    @abc.abstractmethod
    def remove_edge(self, source: Vertex, target: Vertex) -> None:
        """Remove an edge from the permission graph."""
