Permission-graph provides an authorization framework for granular access control.

## Getting started

Fundamentally, permission-graph helps authorize **Actors** to take **Actions**
on **Resources**. Take the following example of an actor named Alice and a 
simple file system. 

The graph defines a **ResourceType** named  "Document" with two **Actions**: 
`ViewDocument` and `EditDocument`.

There are two **Resources** created, each representing a file in the file 
system: `cc_info.csv` and `passwords.txt`. Each resource has its own copy of the
actions defined by its resource type.

Finally, an **Actor** named "Alice" is defined, with "Allow" links to the
actions of `cc_info.csv`. The allow link indicates that Alice is authorized
to perform the ViewDocument and EditDocument actions on the file. Meanwhile,
the missing links to the actions of `passwords.txt` indicate Alice does not have
permission to perform those actions.

=== "Diagram"
    ```mermaid
    flowchart
        alice[actor:Alice]
        document_type[resource_type:Document]
        document[resource:Document:cc_info.csv]
        document2[resource:Document:passwords.txt]
        view_d1[action:ViewDocument]
        edit_d1[action:EditDocument]
        view_d2[action:ViewDocument]
        edit_d2[action:EditDocument]
        document-->|member of|document_type
        document2-->|member of|document_type

        view_d1-->|member of|document
        edit_d1-->|member of|document
        view_d2-->|member of|document2
        edit_d2-->|member of|document2

        alice-->|allow|view_d1
        alice-->|allow|edit_d1


        style alice fill:#227aff,color:#FFF
        style view_d1 fill:#0F0
        style edit_d1 fill:#0F0
        style view_d2 fill:#0F0
        style edit_d2 fill:#0F0
        style document fill:#eef95a
        style document2 fill:#eef95a
        style document_type fill:#f8b1de
        linkStyle 7 stroke:#0f0,stroke-width:4px,color:green;
        linkStyle 6 stroke:#0f0,stroke-width:4px,color:green;
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

    pg = PermissionGraph()

    alice = Actor(name="Alice")
    pg.add_actor(alice)

    document_type = ResourceType(name="Document", actions=["ViewDocument", "EditDocument"])
    pg.add_resource_type(document_type)

    cc_info = Resource(name="cc_info.csv", resource_type="Document")
    pg.add_resource(cc_info)
    passwords = Resource(name="passwords.txt", resource_type="Document")
    pg.add_resource(passwords)

    view_cc_info = Action(name="ViewDocument", resource_type="Document", resource="cc_info.csv")
    edit_cc_info = Action(name="EditDocument", resource_type="Document", resource="cc_info.csv")
    view_passwords = Action(name="ViewDocument", resource_type="Document", resource="passwords.txt")
    edit_passwords = Action(name="EditDocument", resource_type="Document", resource="passwords.txt")

    pg.allow(alice, view_cc_info)
    pg.allow(alice, edit_cc_info)
    
    assert pg.action_is_authorized(alice, view_cc_info) is True, "Alice is authorized to view cc_info"
    assert pg.action_is_authorized(alice, edit_cc_info) is True, "Alice is authorized to edit cc_info"
    assert pg.action_is_authorized(alice, view_passwords) is False, "Alice is not authorized to view passwords"
    assert pg.action_is_authorized(alice, edit_passwords) is False, "Alice is not authorized to edit passwords"
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
        view[action:ViewDocument]
        edit[action:EditDocument]
        document_type[resource_type:Document]

        document-->|member of|document_type

        view-->|member of|document
        edit-->|member of|document

        alice-->|allow|view
        alice-->|allow|edit
        bob-->|allow|view
        bob-->|allow|edit


        style alice fill:#227aff,color:#FFF
        style bob fill:#227aff,color:#FFF
        style view fill:#0F0
        style edit fill:#0F0
        style document fill:#eef95a
        style document_type fill:#f8b1de
        linkStyle 3 stroke:#0f0,stroke-width:4px,color:green;
        linkStyle 4 stroke:#0f0,stroke-width:4px,color:green;
        linkStyle 5 stroke:#0f0,stroke-width:4px,color:green;
        linkStyle 6 stroke:#0f0,stroke-width:4px,color:green;
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

    pg = PermissionGraph()

    alice = Actor(name="Alice")
    pg.add_actor(alice)

    document_type = ResourceType(name="Document", actions=["ViewDocument", "EditDocument"])
    pg.add_resource_type(document_type)

    bob = Actor(name="Bob")
    pg.add_actor(bob)

    document = Resource(name="cc_info.csv", resource_type="Document")
    pg.add_resource(document)

    view_cc_info = Action(name="ViewDocument", resource_type="Document", resource="cc_info.csv")
    edit_cc_info = Action(name="EditDocument", resource_type="Document", resource="cc_info.csv")

    pg.allow(alice, view_cc_info)
    pg.allow(alice, edit_cc_info)

    pg.allow(bob, view_cc_info)
    pg.allow(bob, edit_cc_info)
    
    assert pg.action_is_authorized(alice, view_cc_info) is True, "Alice is authorized to view cc_info"
    assert pg.action_is_authorized(alice, edit_cc_info) is True, "Alice is authorized to edit cc_info"
    assert pg.action_is_authorized(bob, view_cc_info) is True, "Bob is authorized to view cc_info"
    assert pg.action_is_authorized(bob, edit_cc_info) is True, "Bob is authorized to edit cc_info"
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
        view[action:ViewDocument]
        edit[action:EditDocument]
        document_type[resource_type:Document]
        
        document-->|member of|document_type

        view-->|member of|document
        edit-->|member of|document

        alice-->|member of|accountants
        bob-->|member of|accountants

        accountants-->|allow|view
        accountants-->|allow|edit

        style alice fill:#227aff,color:#FFF
        style bob fill:#227aff,color:#FFF
        style view fill:#0F0
        style edit fill:#0F0
        style document fill:#eef95a
        style document_type fill:#f8b1de
        style accountants fill:#fdebdf
        linkStyle 3 stroke:#0f0,stroke-width:4px,color:green;
        linkStyle 4 stroke:#0f0,stroke-width:4px,color:green;
        linkStyle 5 stroke:#0f0,stroke-width:4px,color:green;
        linkStyle 6 stroke:#0f0,stroke-width:4px,color:green;
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

    pg = PermissionGraph()

    alice = Actor(name="Alice")
    pg.add_actor(alice)

    document_type = ResourceType(name="Document", actions=["ViewDocument", "EditDocument"])
    pg.add_resource_type(document_type)

    bob = Actor(name="Bob")
    pg.add_actor(bob)

    accountants = Group(name="Accountants")
    pg.add_group(accountants)

    pg.add_actor_to_group(alice, accountants)
    pg.add_actor_to_group(bob, accountants)

    document = Resource(name="cc_info.csv", resource_type="Document")
    pg.add_resource(document)

    view_cc_info = Action(name="ViewDocument", resource_type="Document", resource="cc_info.csv")
    edit_cc_info = Action(name="EditDocument", resource_type="Document", resource="cc_info.csv")

    pg.allow(accountants, view_cc_info)
    pg.allow(accountants, edit_cc_info)
    
    assert pg.action_is_authorized(alice, view_cc_info) is True, "Alice is authorized to view cc_info"
    assert pg.action_is_authorized(alice, edit_cc_info) is True, "Alice is authorized to edit cc_info"
    assert pg.action_is_authorized(bob, view_cc_info) is True, "Bob is authorized to view cc_info"
    assert pg.action_is_authorized(bob, edit_cc_info) is True, "Bob is authorized to edit cc_info"
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
        view[action:ViewDocument]
        edit[action:EditDocument]
        document_type[resource_type:Document]
        
        document-->|member of|document_type

        view-->|member of|document
        edit-->|member of|document

        alice-->|member of|accountants
        bob-->|member of|accountants

        accountants-->|allow|view
        accountants-->|allow|edit

        bob-->|deny|edit


        style alice fill:#227aff,color:#FFF
        style bob fill:#227aff,color:#FFF
        style view fill:#0F0
        style edit fill:#0F0
        style document fill:#eef95a
        style document_type fill:#f8b1de
        style accountants fill:#fdebdf
        linkStyle 3 stroke:#0f0,stroke-width:4px,color:green;
        linkStyle 4 stroke:#0f0,stroke-width:4px,color:green;
        linkStyle 5 stroke:#0f0,stroke-width:4px,color:green;
        linkStyle 6 stroke:#0f0,stroke-width:4px,color:green;
        linkStyle 7 stroke:#f00,stroke-width:4px,color:red;
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

    pg = PermissionGraph()

    alice = Actor(name="Alice")
    pg.add_actor(alice)

    bob = Actor(name="Bob")
    pg.add_actor(bob)

    document_type = ResourceType(name="Document", actions=["ViewDocument", "EditDocument"])
    pg.add_resource_type(document_type)

    accountants = Group(name="Accountants")
    pg.add_group(accountants)

    pg.add_actor_to_group(alice, accountants)
    pg.add_actor_to_group(bob, accountants)

    document = Resource(name="cc_info.csv", resource_type="Document")
    pg.add_resource(document)

    view_cc_info = Action(name="ViewDocument", resource_type="Document", resource="cc_info.csv")
    edit_cc_info = Action(name="EditDocument", resource_type="Document", resource="cc_info.csv")

    pg.allow(accountants, view_cc_info)
    pg.allow(accountants, edit_cc_info)
    pg.deny(bob, edit_cc_info)
    
    assert pg.action_is_authorized(alice, view_cc_info) is True, "Alice is authorized to view cc_info"
    assert pg.action_is_authorized(alice, edit_cc_info) is True, "Alice is authorized to edit cc_info"
    assert pg.action_is_authorized(bob, view_cc_info) is True, "Bob is authorized to view cc_info"
    assert pg.action_is_authorized(bob, edit_cc_info) is False, "Bob is not authorized to edit cc_info"
    ``` 

There are two valid paths from Bob to the `EditDocument` permission. 

- Bob --(member_of)-> Accountants --(allow)-> EditDocument
- Bob --(deny)-> EditDocument

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

## Action Propagation

Similar to how groups provide a mechanism to bulk apply permissions for actors,
action propagation allows access to one action to also grant access to 
a different action.

As one example, consider adding a new resource type to our graph named `Directory`
to represent a container for `Document` resources. 

In this case, when user is granted permission to read a directory we expect
the to be granted similar permissions on the files within that directory. If
a user has "Read" access to a directory, they should also have "Read" access
to the files within that directory.

PermisisonGraph doesn't force this "action propagation" behavior, but it does
provide a mechanism to easily implement it if desired.

For simplicity, only the view permission is shown here.


=== "Diagram"
    ```mermaid
    flowchart
        alice[actor:Alice]
        directory_type[resource_type:Directory]
        directory[resource:Directory:Private]
        document_type[resource_type:Document]
        document[resource:Document:cc_info.csv]
        view_document[action:ViewDocument]
        view_directory[action:ViewDirectory]
        
        
        directory-->|member of|directory_type
        document-->|member of|document_type

        view_document-->|member of|document
        view_directory-->|member of|directory

        view_directory-->|allow|view_document

        alice-->|allow|view_directory

        style alice fill:#227aff,color:#FFF
        style view_document fill:#0F0
        style view_directory fill:#0F0
        style document fill:#eef95a
        style document_type fill:#f8b1de
        style directory fill:#eef95a
        style directory_type fill:#f8b1de
        linkStyle 4 stroke:#0f0,stroke-width:4px,color:green;
        linkStyle 5 stroke:#0f0,stroke-width:4px,color:green;
    ```

=== "Python"
    ```python title="Alice's Directory"
    from permission_graph import PermissionGraph
    from permission_graph.structs import (
        Actor,
        Resource,
        ResourceType,
        Action
    )

    pg = PermissionGraph()

    alice = Actor(name="Alice")
    pg.add_actor(alice)

    document_type = ResourceType(name="Document", actions=["ViewDocument"])
    pg.add_resource_type(document_type)
    directory_type = ResourceType(name="Directory", actions=["ViewDirectory"])
    pg.add_resource_type(directory_type)

    document = Resource(name="cc_info.csv", resource_type="Document")
    pg.add_resource(document)
    view_cc_info = Action(name="ViewDocument", resource_type="Document", resource="cc_info.csv")

    directory = Resource(name="Private", resource_type="Directory")
    pg.add_resource(directory)
    view_directory = Action(name="ViewDirectory", resource_type="Directory", resource="Private")

    pg.allow(view_directory, view_cc_info)
    pg.allow(alice, view_directory)
    
    assert pg.action_is_authorized(alice, view_cc_info) is True, "Alice is authorized to view cc_info"
    ```
