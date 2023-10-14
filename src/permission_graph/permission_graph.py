from permission_graph.backends.base import PermissionGraphBackend
from permission_graph.structs import (
    Action,
    Actor,
    EdgeType,
    Group,
    Resource,
    ResourceType,
    TieBreakerPolicy,
)


class PermissionGraph:
    def __init__(
        self, backend: PermissionGraphBackend, tie_breaker_policy: TieBreakerPolicy = TieBreakerPolicy.ANY_ALLOW
    ) -> None:
        """Initialize a new PermissionGraph."""
        self.resource_types = []
        self.backend = backend
        self.tie_breaker_policy = tie_breaker_policy

    def add_actor(self, actor: Actor) -> None:
        """Add a actor to the permission graph."""
        self.backend.add_vertex(actor)

    def remove_actor(self, actor: Actor) -> None:
        """Remove a actor from the permission graph."""
        self.backend.remove_vertex(actor)

    def register_resource_type(self, resource_type: ResourceType):
        """Register a resource type."""
        if len(resource_type.actions) == 0:
            raise ValueError("A resource type must have at least one action defined.")
        self.resource_types.append(resource_type)

    def add_resource(self, resource: Resource) -> None:
        """Add a resource to the permission graph."""
        if resource.resource_type is None or not isinstance(resource.resource_type, ResourceType):
            raise TypeError(f"Invalid resource_type '{resource.resource_type}'")
        if resource.resource_type not in self.resource_types:
            raise ValueError(
                f"Unrecognized ResourceType: {resource.resource_type}. " "Register with 'register_resource_type'."
            )
        self.backend.add_vertex(resource)
        for action_name in resource.resource_type.actions:
            action = Action(action_name, resource)
            self.backend.add_vertex(action)
            self.backend.add_edge(EdgeType.MEMBER_OF, action, resource)

    def remove_resource(self, resource: Resource) -> None:
        """Remove a resource from the permission graph."""
        actions = self.backend.get_vertices_to(resource)
        self.backend.remove_vertex(resource)
        for action in actions:
            self.backend.remove_vertex(action)

    def add_group(self, group: Group):
        """Add a group to the permission graph."""
        self.backend.add_vertex(group)

    def remove_group(self, group: Group):
        """Remove a group from the permission graph."""
        self.backend.remove_vertex(group)

    def allow(self, actor: Actor | Group | Action, action: Action):
        """Grant actor or group permission to take action on resource or group."""
        self.backend.add_edge(EdgeType.ALLOW, source=actor, target=action)

    def deny(self, actor: Actor | Group | Action, action: Action):
        """Deny actor or group permission to take action on resource or group."""
        self.backend.add_edge(EdgeType.DENY, source=actor, target=action)

    def revoke(self, actor: Actor | Group | Action, action: Action):
        """Revoke a permission (either allow or deny)."""
        self.backend.remove_edge(actor, action)

    def add_actor_to_group(self, actor: Actor, group: Group):
        """Add a actor to a group."""
        self.backend.add_edge(EdgeType.MEMBER_OF, source=actor, target=group)

    def remove_actor_from_group(self, actor: Actor, group: Group):
        """Remove a actor from a group."""
        self.backend.remove_edge(source=actor, target=group)

    def describe_actor_permissions(self, actor: Actor):
        """Describe a actor's permissions."""
        raise NotImplementedError

    def describe_resource_permissions(self, resource: Resource):
        """Describe a resource's permissions."""
        raise NotImplementedError

    def action_is_authorized(self, actor: Actor, action: str) -> bool:
        """Authorize actor to perform action on resource."""
        shortest_paths = self.backend.shortest_paths(actor, action)
        if len(shortest_paths) == 0:
            return False
        elif len(shortest_paths) == 1:
            shortest_path = shortest_paths[0]
            return self.backend.get_edge_type(shortest_path[-2], shortest_path[-1]) == EdgeType.ALLOW
        else:
            match self.tie_breaker_policy:
                case TieBreakerPolicy.ANY_ALLOW:
                    policy = any
                case TieBreakerPolicy.ALL_ALLOW:
                    policy = all
            return policy(self.backend.get_edge_type(path[-2], path[-1]) == EdgeType.ALLOW for path in shortest_paths)
