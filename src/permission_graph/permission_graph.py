from typing import Type

from permission_graph.backends.base import PermissionGraphBackend
from permission_graph.backends.igraph import IGraphMemoryBackend
from permission_graph.structs import (
    Action,
    Actor,
    EdgeType,
    Group,
    Resource,
    ResourceType,
    TieBreakerPolicy,
    Vertex,
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
        self.backend.add_vertex(resource)
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

    def paths_to_targets(
        self,
        source: Vertex,
        target_vtype: Type | tuple[Type],
        prefix: list[Vertex],
        paths: list[list[Vertex]],
        reverse=False,
    ) -> list[list[Vertex]]:
        """Finds paths from a source vertex to other vertices of specified type.

        This is a helpful utility for traversing the permissions graph. You can
        use it, for example, to find all of the Actions granted to a User or
        Group, or to find all of the users and groups allowed to perform some
        Action.

        To prevent unexpectedly expensive invocations, search along a path will
        not proceed beyond the first occurrence of a target_vtype. This means
        that if looking for all Actions that a user is granted permission to
        access, it will return any Actions that are granted directly to a User
        or to a Group the user is a part of. However, it will not return
        downstream actions granted via action propagation. Similarly, if looking
        for all Users and Groups with access to a particular Resource, the search
        will stop will return a path to a Group, but it will not return a path
        to all users within that group. Expanding those paths is possible
        through subsequent invocations of this function.

        Args:
            source: The source vertex to find paths from
            target_vtype: The type(s) of vertices to look for. For any path,
                search will terminate with first node of specified type.
            prefix: The nodes already part of this path
            paths: list to which to append paths
            reverse: if True, will look backwards through the directed graph
                (default False).
        """
        if reverse:
            targets = self.backend.get_vertices_to(source)
        else:
            targets = self.backend.get_vertices_from(source)

        # Recursively invoke on children
        new_prefix = prefix + [source]
        for target in targets:
            if isinstance(target, target_vtype):
                path = new_prefix + [target]
                paths.append(path[::-1])
            else:
                self._paths_to_targets(
                    target, target_vtype=target_vtype, prefix=new_prefix, paths=paths, reverse=reverse
                )

        return paths

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

    def update_resource_type_actions(self, resource_type_name: str, new_actions: list[str]):
        """Update the set of actions supported by ResourceType.

        This method updates the ResourceType definition, and updates all existing
        resources of this resource type.

        Args:
            resource_type_name: The name of the resource type to update
            new_actions: A full list of actions supported by this resource type
        """
        resource_type = self.backend.vertex_factory(f"resource_type:{resource_type_name}")
        self.backend.update_vertex_attributes(resource_type=resource_type, actions=new_actions)
        old_action_set = set(resource_type.actions)
        new_action_set = set(new_actions)
        actions_to_add = new_action_set.difference(old_action_set)
        actions_to_remove = old_action_set.difference(new_action_set)
        resources = self.backend.get_vertices_to(resource_type)
        for resource in resources:
            # Add actions_to_add
            for action_name in actions_to_add:
                action = Action(name=action_name, resource_type=resource_type_name, resource=resource.name)
                self.backend.add_vertex(action)
                self.backend.add_edge(EdgeType.MEMBER_OF, action, resource)

            # Remove actions_to_remove
            for action_name in actions_to_remove:
                action = Action(
                    name=action_name,
                    resource_type=resource_type_name,
                    resource=resource.name,
                )
                self.backend.remove_vertex(action)
