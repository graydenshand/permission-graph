from permission_graph.backends.base import PermissionGraphBackend
from permission_graph.backends.igraph import IGraphMemoryBackend
from permission_graph.structs import (
    Action,
    Actor,
    EdgeType,
    Group,
    PermissionPolicy,
    Resource,
    ResourceType,
    TieBreakerPolicy,
)


class PermissionGraph:
    def __init__(
        self, backend: PermissionGraphBackend = None, tie_breaker_policy: TieBreakerPolicy = TieBreakerPolicy.ANY_ALLOW
    ) -> None:
        """Initialize a new PermissionGraph."""
        if backend is None:
            backend = IGraphMemoryBackend()
        self.backend = backend
        self.tie_breaker_policy = tie_breaker_policy
        self._resource_type_map = {}

    def add_actor(self, actor: Actor | str) -> None:
        """Add a actor to the permission graph."""
        self.backend.add_vertex(actor)

    def remove_actor(self, actor: Actor) -> None:
        """Remove a actor from the permission graph."""
        self.backend.remove_vertex(actor)

    def add_resource_type(self, resource_type: ResourceType):
        """Register a resource type to the permission graph."""
        self.backend.add_vertex(resource_type, actions=resource_type.actions)

    def remove_resource_type(self, resource_type: ResourceType):
        """Remove a resource type from the permission graph."""
        for resource in self.backend.get_vertices_to(resource_type):
            self.remove_resource(resource)
        self.backend.remove_vertex(resource_type)

    def add_resource(self, resource: Resource) -> None:
        """Add a resource to the permission graph."""
        resource_type = self.backend.vertex_factory(f"resource_type:{resource.resource_type}")
        self.backend.add_vertex(resource, resource_type=resource.resource_type)
        self.backend.add_edge(EdgeType.MEMBER_OF, resource, resource_type)
        for action_name in resource_type.actions:
            action = Action(name=action_name, resource_type=resource.resource_type, resource=resource.name)
            self.backend.add_vertex(action)
            self.backend.add_edge(EdgeType.MEMBER_OF, action, resource)

    def remove_resource(self, resource: Resource) -> None:
        """Remove a resource from the permission graph."""
        actions = self.backend.get_vertices_to(resource)
        for action in actions:
            self.backend.remove_vertex(action)
        self.backend.remove_vertex(resource)

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

    def describe_actor_permissions(self, actor: Actor) -> list[PermissionPolicy]:
        """Describe an actor's permissions.

        Returns:
            A list of objects:
                - action: Action
                - actor: Actor
                - path: list[Vertex]
        """
        raise NotImplementedError

    def describe_resource_permissions(self, resource: Resource) -> list[PermissionPolicy]:
        """Describe permissions on a resource.

        Returns:
            A list of objects:
                - action: Action
                - actor: Actor
                - path: list[Vertex]
        """
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

    def update_resource_type(self, resource_type_name: str, new_actions: list[str]):
        """Update the set of actions supported by ResourceType.

        This method updates the ResourceType definition, and updates all existing
        resources of this resource type.
        """
        resources = self.backend.get_vertices_by_prefix(f"resource:{resource_type_name}:")
        raise NotImplementedError
