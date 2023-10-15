Permission-graph provides an authorization framework for granular access control.

## Getting started

Fundamentally, permission-graph helps authorize **Actors** to take **Actions**
on **Resources**. Take the following example of an actor named Alice and a sensitive
csv file. The graph defines a **ResourceType** named  "Document" with three actions:

* `ViewDocument`
* `EditDocument`
* `ShareDocument`

`cc_info.csv` is an instance of the "Document" resource type; in the permission graph,
the its vertex it is connected to the resource type vertex with a `member_of` 
edge to reflect this relationship.


=== "Diagram"
    ```mermaid
    flowchart
        alice[actor:Alice]
        document_type[resource_type:Document]
        document[resource:Document:cc_info.csv]
        read[action:ViewDocument]
        write[action:EditDocument]
        share[action:ShareDocument]

        document-->|member of|document_type

        read-->|member of|document
        write-->|member of|document
        share-->|member of|document

        alice-->|allow|read
        alice-->|allow|write
        alice-->|allow|share
    ```

=== "Python"
    ```python title="Alice's Document"
    from permission_graph import PermissionGraph
    from permission_graph.structs import (
        Actor,
        Resource,
        ResourceType,
        Action
    )

    # An empty `PermissionGraph` is created, using the default in-memory 
    # backend built on igraph.

    pg = PermissionGraph()

    # A ResourceType named "Document" is registered with three actions.

    document_type = ResourceType(
        name="Document", 
        actions=[
            "ViewDocument", 
            "EditDocument",
            "ShareDocument"
        ]
    )
    pg.add_resource_type(document_type)

    # And `Actor` with a name "Alice" is created. An Actor is an entity that 
    # will act on resources. It could represent a human user, as in this example,
    # or a service/machine.

    alice = Actor(name="Alice")
    pg.add_actor(alice)

    # A resource named "cc_info.csv" is registered. It references the "Document" 
    # resource type that was created above. A node is created in the permission
    # graph for the resource and each of its actions as defined by its resource type.

    document = Resource(name="cc_info.csv", resource_type="Document")
    pg.add_resource(document)

    view = Action(name="ViewDocument", resource_type="Document", resource="cc_info.csv")
    edit = Action(name="EditDocument", resource_type="Document", resource="cc_info.csv")
    share = Action(name="ShareDocument", resource_type="Document", resource="cc_info.csv")

    # Grant permissions

    pg.allow(alice, view)
    pg.allow(alice, edit)
    pg.allow(alice, share)
    
    # Validate permissions

    assert pg.action_is_authorized(alice, view) is True, "Alice is authorized to view"
    assert pg.action_is_authorized(alice, edit) is True, "Alice is authorized to edit"
    assert pg.action_is_authorized(alice, share) is True, "Alice is authorized to share"
    ```

## Groups

Groups are used to share permissions with many users.

Continuing from the example above, say we add another user named Bob whom
we also wish to have full access to the `cc_info.csv` document. 

One way to accomplish this is to add the same permissions that we did for Alice.


=== "Diagram"
    ```mermaid
    flowchart
        alice[actor:Alice]
        bob[actor:Bob]
        document[resource:cc_info.csv]
        read[action:ReadDocument]
        write[action:WriteDocument]
        share[action:ShareDocument]
        document_type[resource_type:Document]

        document-->|member of|document_type

        read-->|member of|document
        write-->|member of|document
        share-->|member of|document

        alice-->|allow|read
        alice-->|allow|write
        alice-->|allow|share
        bob-->|allow|read
        bob-->|allow|write
        bob-->|allow|share
    ```
=== "Python"
    ```python title="Two users"
    from permission_graph import PermissionGraph
    from permission_graph.structs import (
        Actor,
        Resource,
        ResourceType,
        Action
    )

    # An empty `PermissionGraph` is created, using the default in-memory 
    # backend built on igraph.

    pg = PermissionGraph()

    # A ResourceType named "Document" is registered with three actions.

    document_type = ResourceType(
        name="Document", 
        actions=[
            "ViewDocument", 
            "EditDocument",
            "ShareDocument"
        ]
    )
    pg.add_resource_type(document_type)

    # Two actors named Alice and Bob are created.

    alice = Actor(name="Alice")
    pg.add_actor(alice)

    bob = Actor(name="Bob")
    pg.add_actor(bob)

    # A resource named "cc_info.csv" is registered. It references the "Document" 
    # resource type that was created above. A node is created in the permission
    # graph for the resource and each of its actions as defined by its resource type.

    document = Resource(name="cc_info.csv", resource_type="Document")
    pg.add_resource(document)

    view = Action(name="ViewDocument", resource_type="Document", resource="cc_info.csv")
    edit = Action(name="EditDocument", resource_type="Document", resource="cc_info.csv")
    share = Action(name="ShareDocument", resource_type="Document", resource="cc_info.csv")

    # Grant permissions

    pg.allow(alice, view)
    pg.allow(alice, edit)
    pg.allow(alice, share)

    pg.allow(bob, view)
    pg.allow(bob, edit)
    pg.allow(bob, share)
    
    # Validate permissions

    assert pg.action_is_authorized(alice, view) is True, "Alice is authorized to view"
    assert pg.action_is_authorized(alice, edit) is True, "Alice is authorized to edit"
    assert pg.action_is_authorized(alice, share) is True, "Alice is authorized to share"
    assert pg.action_is_authorized(bob, view) is True, "Bob is authorized to view"
    assert pg.action_is_authorized(bob, edit) is True, "Bob is authorized to edit"
    assert pg.action_is_authorized(bob, share) is True, "Bob is authorized to share"
    ```

This may work fine for some applications, but Groups provide a means to share the
same set of permission policies among many users.

=== "Diagram"
    ```mermaid
    flowchart
        alice[actor:Alice]
        bob[actor:Bob]
        accountants[group:Accountants]
        document[resource:cc_info.csv]
        read[action:ReadDocument]
        write[action:WriteDocument]
        share[action:ShareDocument]
        document_type[resource_type:Document]
        
        document-->|member of|document_type

        read-->|member of|document
        write-->|member of|document
        share-->|member of|document

        alice-->|member of|accountants
        bob-->|member of|accountants

        accountants-->|allow|read
        accountants-->|allow|write
        accountants-->|allow|share
    ```
=== "Python"
    ```python title="Groups"
    from permission_graph import PermissionGraph
    from permission_graph.structs import (
        Actor,
        Resource,
        ResourceType,
        Action,
        Group
    )

    # An empty `PermissionGraph` is created, using the default in-memory 
    # backend built on igraph.

    pg = PermissionGraph()

    # A ResourceType named "Document" is registered with three actions.

    document_type = ResourceType(
        name="Document", 
        actions=[
            "ViewDocument", 
            "EditDocument",
            "ShareDocument"
        ]
    )
    pg.add_resource_type(document_type)

    # Create actors

    alice = Actor(name="Alice")
    pg.add_actor(alice)

    bob = Actor(name="Bob")
    pg.add_actor(bob)

    # Create a group and add actors to it

    accountants = Group(name="Accountants")
    pg.add_group(accountants)

    pg.add_actor_to_group(alice, accountants)
    pg.add_actor_to_group(bob, accountants)

    # Create the document

    document = Resource(name="cc_info.csv", resource_type="Document")
    pg.add_resource(document)

    view = Action(name="ViewDocument", resource_type="Document", resource="cc_info.csv")
    edit = Action(name="EditDocument", resource_type="Document", resource="cc_info.csv")
    share = Action(name="ShareDocument", resource_type="Document", resource="cc_info.csv")

    # Grant permissions

    pg.allow(accountants, view)
    pg.allow(accountants, edit)
    pg.allow(accountants, share)
    
    # Validate permissions

    assert pg.action_is_authorized(alice, view) is True, "Alice is authorized to view"
    assert pg.action_is_authorized(alice, edit) is True, "Alice is authorized to edit"
    assert pg.action_is_authorized(alice, share) is True, "Alice is authorized to share"
    assert pg.action_is_authorized(bob, view) is True, "Bob is authorized to view"
    assert pg.action_is_authorized(bob, edit) is True, "Bob is authorized to edit"
    assert pg.action_is_authorized(bob, share) is True, "Bob is authorized to share"
    ```

## Deny Permissions

We've already seen two of the three supported edge types in permission-graph:

- `MEMBER_OF`: Indicates one vertex is a member of another (e.g. an actor is a member of a group)
- `ALLOW`: Indicates one vertex is allowed to perform some action

The third edge type is `DENY`, which is analagous to `ALLOW` but explicitly does not
allow an actor to perform some action.

To understand why this is useful, we continue from our example above. Bob and
Alice both belong to the Accountants group, which grants them full access to 
the "cc_info.csv" document.

But what if we wanted to revoke Bob's permission to share the document with
others? One approach is to go back to managing each actor's permisisons
individually.

However, we can also use a `DENY` edge to accomplish the same end, while keeping
our graph lean.

=== "Diagram"
    ```mermaid
    flowchart
        alice[actor:Alice]
        bob[actor:Bob]
        accountants[group:Accountants]
        document[resource:cc_info.csv]
        read[action:ReadDocument]
        write[action:WriteDocument]
        share[action:ShareDocument]
        document_type[resource_type:Document]
        
        document-->|member of|document_type

        read-->|member of|document
        write-->|member of|document
        share-->|member of|document

        alice-->|member of|accountants
        bob-->|member of|accountants

        accountants-->|allow|read
        accountants-->|allow|write
        accountants-->|allow|share

        bob-->|deny|share
    ```
=== "Python"
    ```python title="Deny permissions"
    from permission_graph import PermissionGraph
    from permission_graph.structs import (
        Actor,
        Resource,
        ResourceType,
        Action,
        Group
    )

    # An empty `PermissionGraph` is created, using the default in-memory 
    # backend built on igraph.

    pg = PermissionGraph()

    # A ResourceType named "Document" is registered with three actions.

    document_type = ResourceType(
        name="Document", 
        actions=[
            "ViewDocument", 
            "EditDocument",
            "ShareDocument"
        ]
    )
    pg.add_resource_type(document_type)

    # Create actors

    alice = Actor(name="Alice")
    pg.add_actor(alice)

    bob = Actor(name="Bob")
    pg.add_actor(bob)

    # Create a group and add actors to it

    accountants = Group(name="Accountants")
    pg.add_group(accountants)

    pg.add_actor_to_group(alice, accountants)
    pg.add_actor_to_group(bob, accountants)

    # Create the document

    document = Resource(name="cc_info.csv", resource_type="Document")
    pg.add_resource(document)

    view = Action(name="ViewDocument", resource_type="Document", resource="cc_info.csv")
    edit = Action(name="EditDocument", resource_type="Document", resource="cc_info.csv")
    share = Action(name="ShareDocument", resource_type="Document", resource="cc_info.csv")

    # Grant permissions

    pg.allow(accountants, view)
    pg.allow(accountants, edit)
    pg.allow(accountants, share)
    pg.deny(bob, share)
    
    # Validate permissions

    assert pg.action_is_authorized(alice, view) is True, "Alice is authorized to view"
    assert pg.action_is_authorized(alice, edit) is True, "Alice is authorized to edit"
    assert pg.action_is_authorized(alice, share) is True, "Alice is authorized to share"
    assert pg.action_is_authorized(bob, view) is True, "Bob is authorized to view"
    assert pg.action_is_authorized(bob, edit) is True, "Bob is authorized to edit"
    assert pg.action_is_authorized(bob, share) is False, "Bob is not authorized to share"
    ``` 

There are two valid paths from Bob to the `ShareDocument` permission. 

- Bob --> Accountants --(allow)-> ShareDocument
- Bob --(deny)-> ShareDocument

Through his membership in the Accountants group, he is allowed to share the document. However,
the most direct path between Bob and the document denies access, so Bob will not
be allowed to share the document with others.

This example demonstrates a key principle of permission-graph: **The most direct
permission wins**.

The `action_is_authorized` method works by finding the shortest path from the
actor to the action. The cases are handled as follows:

- If there is no path from actor to the action, the action is not authorized.
- If there is a true shortest path from actor to the action, the action is authorized
    if the edge to the action along that path is an *ALLOW* edge. If the edge is
    a *DENY* edge, the action is not authorized.
- If there are multiple paths of equal length such that there is no one shortest,
    the action uses the `TieBreakerPolicy` to authorize the action. The two
    policies are:
    1. `ANY_ALLOW`: Allow the action if any of the shortest paths allow the action
    2. `ALL_ALLOW`: Allow the action only if all the shortest paths allow the action

    The default policy is `ANY_ALLOW`, but can be set when instantiating the
    PermissionGraph.
    
    ```python title="TieBreakerPolicy"
    from permission_graph import PermissionGraph
    from permission_graph.structs import TieBreakerPolicy

    pg = PermissionGraph(tie_breaker_policy=TieBreakerPolicy.ALL_ALLOW)
    ```