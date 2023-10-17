"""A graph based authorization framework.

The permissions graph consists of Vertices and Edges.

**Vertices**

* `ResourceType`: a type definition for resources describing its supported actions
* `Resource`: a resource with actions requiring authorization
* `Action`: an action on a resource
* `Actor`: an identity that will take actions on resources
* `Group`: a named collection of `Actors` with shared permission policies

**Edges**

* `MemberOf`: indicates membership in a collection
    - `Actor -> MemberOf -> Group`
    - `Action -> MemberOf -> Resource`
    - `Resource -> MemberOf -> ResourceType`
* `Allow`: indicates positive permission to act on a resource
    - `Actor|Group|Action -> Allow -> Action`
* `Deny`: indicates negative permission to act on a resource
    - `Actor|Group|Action -> Deny -> Action`

### Authorizing Access

Authorization to act on a resource is decided by finding the shortest path between
an actor and the action to be performed. If that shortest path is an ALLOW rule, 
the actor is authorized. If that shortest path is a DENY rule, or if there is no
path between the actor and the action, the actor is not authorized.

In the event there is a tie for shortest path, the access will be denied only
if all shortest paths are DENY rules. This behavior can be controlled when
initializing the permission graph via the `tie_breaker_policy` parameter.
"""
from importlib.metadata import version

__version__ = version("permission_graph")

from permission_graph.permission_graph import PermissionGraph
