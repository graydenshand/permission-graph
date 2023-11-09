import json
from typing import Any

import psycopg2

from permission_graph.backends.base import PermissionGraphBackend
from permission_graph.structs import EdgeType, Vertex


class PostgresBackend(PermissionGraphBackend):
    def __init__(self, conn_string: str) -> None:
        """Instantiate a PostgresBackend."""
        self.conn_string = conn_string

    def _execute_queries(self, sql: list[str], params: list[tuple[Any, ...] | dict[str, Any]]) -> list[tuple[Any, ...]]:
        """Execute a series of SQL queries as a transaction, return result of last query."""
        if len(sql) != len(params):
            raise ValueError("Number of sql queries does not match number of parameter groups.")
        with psycopg2.connect(self.conn_string) as conn:
            with conn.cursor() as cursor:
                for i in range(len(sql)):
                    cursor.execute(sql[i], params[i])
                try:
                    results = cursor.fetchall()
                except psycopg2.ProgrammingError:
                    results = []
            conn.commit()
            return results

    def _execute_query(self, sql: str, params: dict[str, Any] | tuple[Any, ...]) -> list[tuple[Any, ...]]:
        """Execute a SQL query."""
        return self._execute_queries([sql], [params])

    def add_vertex(self, vertex: Vertex, **kwargs) -> None:
        """Add a vertex to the permission graph.

        Raises ValueError if vertex already exists.
        """
        sql = "INSERT INTO vertices (id, vtype, attrs) VALUES (%s, %s, %s);"
        params = (vertex.id, vertex.vtype, json.dumps(kwargs))
        try:
            self._execute_query(sql, params)
        except psycopg2.errors.UniqueViolation:
            raise ValueError("Vertex already exists")

    def remove_vertex(self, vertex: Vertex, **kwargs) -> None:
        """Remove a vertex from the permission graph."""
        sql = "DELETE FROM vertices WHERE id = %s;"
        params = (vertex.id,)
        self._execute_query(sql, params)

    def vertex_exists(self, vertex: Vertex) -> bool:
        """Check if a vertex with vtype=vtype and id=id already exists."""
        sql = "SELECT id FROM vertices WHERE id = %s;"
        params = (vertex.id,)
        results = self._execute_query(sql, params)
        return len(results) > 0

    def get_vertices_to(self, vertex: Vertex) -> list[Vertex]:
        """Get all vertices that target a vertex."""
        sql = """\
        SELECT source_v
        FROM edges
        WHERE target_v = %s;"""
        params = (vertex.id,)
        results = self._execute_query(sql, params)
        return [self.vertex_factory(row[0]) for row in results]

    def get_vertices_from(self, vertex: Vertex) -> list[Vertex]:
        """Get all vertices that a vertex targets."""
        sql = """\
        SELECT target_v
        FROM edges
        WHERE source_v = %s;"""
        params = (vertex.id,)
        results = self._execute_query(sql, params)
        return [self.vertex_factory(row[0]) for row in results]

    def update_vertex_attributes(self, vertex: Vertex, **kwargs):
        """Update one or more attributes of a vertex."""
        sql = "SELECT attrs FROM vertices WHERE id = %s;"
        params = (vertex.id,)
        results = self._execute_query(sql, params)
        if len(results) == 0:
            raise ValueError("Vertex not found")

        attrs = results[0][0]
        attrs.update(kwargs)

        sql = "UPDATE vertices SET attrs = %s;"
        params = (json.dumps(attrs),)
        self._execute_query(sql, params)

    def add_edge(self, etype: str, source: Vertex, target: Vertex) -> None:
        """Add a edge to the permission graph.

        Args:
            etype: edge type (one of 'member_of', 'allow', 'deny')
            source: source vertex
            target: target vertex
            **kwargs: addition attributes to add to edge

        Raises ValueError if an edge from source to target already exists.
        """
        sql = "INSERT INTO edges (source_v, target_v, etype) VALUES (%s, %s, %s);"
        params = (source.id, target.id, etype.value)
        try:
            self._execute_query(sql, params)
        except psycopg2.errors.UniqueViolation:
            raise ValueError("Edge already exists")

    def edge_exists(self, source: Vertex, target: Vertex) -> bool:
        """Return True if edge exists."""
        sql = "SELECT 1 FROM edges WHERE source_v = %s and target_v = %s;"
        params = (source.id, target.id)
        result = self._execute_query(sql, params)
        return len(result) > 0

    def remove_edge(self, source: Vertex, target: Vertex) -> None:
        """Remove an edge from the permission graph."""
        sql = "DELETE FROM edges WHERE source_v = %s AND target_v = %s;"
        params = (source.id, target.id)
        self._execute_query(sql, params)

    def shortest_paths(self, source: Vertex, target: Vertex) -> list[list[Vertex]]:
        """Return the lists of vertices that make the shortest paths from source to target.

        Returns:
            - If there is a true shortest path (no ties), return a list containing one element
                (the shortest path).
            - Otherwise, return a list containing all of the paths with length equal to the
                shortest path.
        """
        sql = """\
        WITH RECURSIVE connected(source_v, target_v, path) AS (
                SELECT source_v, target_v, ARRAY[source_v, target_v] FROM edges WHERE source_v = %(source)s
            UNION
                SELECT e.source_v, e.target_v, ARRAY_APPEND(c.path, e.target_v)
                FROM edges e, connected c
                WHERE e.source_v = c.target_v
                AND e.source_v != %(target)s
        ),
        ranked(path, rank) AS (
            SELECT path,
            rank() OVER (ORDER BY ARRAY_LENGTH(path, 1)) as rank
            FROM connected
            WHERE path[array_upper(path, 1)] = %(target)s
        )
        SELECT path
        FROM ranked
        WHERE rank = 1;
        """
        params = {"source": source.id, "target": target.id}
        results = self._execute_query(sql, params)
        paths = []
        for row in results:
            path = [self.vertex_factory(v) for v in row[0]]
            paths.append(path)
        return paths

    def get_edge_type(self, source: Vertex, target: Vertex) -> EdgeType:
        """Return the EdgeType of the edge connecting two vertices.

        Raises ValueError if there is no edge between the two vertices.
        """
        sql = "SELECT etype FROM edges WHERE source_v = %s AND target_v = %s;"
        params = (source.id, target.id)
        results = self._execute_query(sql, params)
        if len(results) == 0:
            raise ValueError("Edge not found")
        return EdgeType(results[0][0])

    def vertex_factory(self, vertex_id) -> Vertex:
        """Return a vertex from a vertex id.

        Given a vertex id, return an vertex object of the appropriate subclass.
        """
        sql = "SELECT attrs FROM vertices WHERE id = %s;"
        params = (vertex_id,)
        results = self._execute_query(sql, params)
        if len(results) == 0:
            raise ValueError("Vertex not found")
        return Vertex.factory(vertex_id, **results[0][0])

    def init_db(self):
        """Initialize a database with perimission graph tables."""
        sql = []

        sql.append("CREATE TYPE vtype AS ENUM ('actor', 'group', 'resource', 'resource_type', 'action');")

        sql.append("CREATE TYPE etype AS ENUM ('MEMBER_OF', 'ALLOW', 'DENY');")

        sql.append(
            """\
        CREATE TABLE vertices (
            id TEXT PRIMARY KEY,
            vtype vtype NOT NULL,
            attrs JSONB
        );"""
        )

        sql.append(
            """\
        CREATE TABLE edges (
            source_v TEXT REFERENCES vertices(id) ON DELETE CASCADE,
            target_v TEXT REFERENCES vertices(id) ON DELETE CASCADE,
            etype etype NOT NULL,
            PRIMARY KEY (source_v, target_v)
        );"""
        )

        params = [tuple()] * len(sql)
        self._execute_queries(sql, params)
