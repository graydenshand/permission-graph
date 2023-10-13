# permission-graph

A graph based authorization library


## Overview

The permissions graph consists of Vertices and Edges.

**Vertices**

* `Resource`: a resource with predefined actions requiring authorization
* `User`: an identity that will take actions on resources
* `Group`: a named collection of `Users`
* `Action`: an action on a resource

**Edges**

* `MemberOf`: indicates membership in a collection
    - `User -> MemberOf -> Group`
    - `Action -> MemberOf -> Resource`
* `Allow`: indicates positive permission to act on a resource
    - `User -> Allow -> Action`
    - `Group -> Allow -> Action`
* `Deny`: indicates negative permission to act on a resource
    - `User -> Deny -> Action`
    - `Group -> Deny -> Action`

### Authorizing Access

Authorization to act on a resource is decided by finding the shortest path between
a user and the action to be performed. If that shortest path is a positive
permission ("Allow"), the user is authorized. If that shortest path is a
negative permission ("Deny"), or if there is no path between
the user and the action, the user is not authorized.

