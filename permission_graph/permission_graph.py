from permission_graph.backends import PermissionGraphBackend
from permission_graph.structs import (EdgeType, Group, Resource, ResourceType,
                                      User, Vertex)


class PermissionGraph:
    def __init__(self, backend: PermissionGraphBackend) -> None:
        """Initialize a new PermissionGraph."""
        self.resource_types = []
        self.backend = backend

    def validate_vertex(self, vertex: Vertex):
        """Validate a new vertex can be inserted."""
        if self.backend.vertex_exists(vertex):
            raise ValueError(f"Vertex already exists: '{vertex}'")
        if isinstance(vertex, Resource):
            if vertex.resource_type is None:
                raise ValueError("Attempted to add resource with no resource_type.")

    def add_user(self, user: User) -> None:
        """Add a user to the permission graph."""
        self.validate_vertex(user)
        self.backend.add_vertex(user)

    def remove_user(self, user: User) -> None:
        """Remove a user from the permission graph."""
        self.backend.remove_vertex(user)

    def add_resource(self, resource: Resource) -> None:
        """Add a resource to the permission graph."""
        self.validate_vertex(resource)
        if resource.resource_type not in self.resource_types:
            self.resource_types.append(resource.resource_type)
        self.backend.add_vertex(resource)

    def remove_resource(self, resource: Resource) -> None:
        """Remove a resource from the permission graph."""
        self.backend.remove_vertex(resource)

    def add_group(self, group: Group):
        """Add a group to the permission graph."""
        self.validate_vertex(group)
        self.backend.add_vertex(group)

    def remove_group(self, group: Group):
        """Remove a group from the permission graph."""
        self.backend.remove_vertex(group)

    def validate_edge(
        self, etype: EdgeType, source: User | Group, target: Group | Resource, action: str | None = None
    ) -> None:
        """Validate a new edge.

        Args:
            - etype: edge type (one of 'member_of', 'allow', 'deny')
            - source: tuple of (vtype, id) for source vertex
            - target: tuple of (vtype, id) for target vertex
            - **kwargs: edge attributes defined as key value pairs
        """
        if etype == EdgeType.MEMBER_OF:
            if not (isinstance(source, User) and isinstance(target, Group)):
                raise ValueError(
                    f"Incompatible vertices for edge type. '{source.vtype}' cannot be a member of '{target.vtype}'"
                )
        if etype in (EdgeType.ALLOW, EdgeType.DENY):
            if not isinstance(source, (User, Group)):
                raise ValueError(f"Invalid vtype for edge source: '{source}'")
            if not isinstance(target, Resource):
                raise ValueError(f"Invalid vtype for edge target: '{target}'")
            if action not in target.resource_type.actions:
                raise ValueError(f"Invalid action for target '{target}': '{action}'")
        if self.backend.edge_exists(source, target):
            raise ValueError(f"An edge already exists between {source} and {target}")

    def allow(self, user_or_group: User | Group, resource: Resource, action: str):
        """Grant user or group permission to take action on resource or group."""
        self.validate_edge(EdgeType.ALLOW, source=user_or_group, target=resource, action=action)
        self.backend.add_edge(EdgeType.ALLOW, source=user_or_group, target=resource, action=action)

    def deny(self, user_or_group: User | Group, resource: Resource, action: str):
        """Deny user or group permission to take action on resource or group."""
        self.validate_edge(EdgeType.DENY, source=user_or_group, target=resource, action=action)
        self.backend.add_edge(EdgeType.DENY, source=user_or_group, target=resource, action=action)

    def revoke(self, user_or_group: User | Group, resource: Resource, action: str):
        """Revoke a permission (either allow or deny)."""
        self.backend.remove_edge(user_or_group, resource)

    def add_user_to_group(self, user: User, group: Group):
        """Add a user to a group."""
        self.validate_edge(EdgeType.MEMBER_OF, source=user, target=group)
        self.backend.add_edge(EdgeType.MEMBER_OF, source=user, target=group)

    def remove_user_from_group(self, user: User, group: Group):
        """Remove a user from a group."""
        self.backend.remove_edge(source=user, target=group)

    def describe_user_permissions(self, user: User):
        """Describe a user's permissions."""
        raise NotImplementedError

    def describe_resource_permissions(self, resource: Resource):
        """Describe a resource's permissions."""
        raise NotImplementedError

    def action_is_authorized(self, user: User, resource: Resource, action: str) -> bool:
        """Authorize user to perform action on resource."""
        raise NotImplementedError
