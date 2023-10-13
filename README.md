# permission-graph

A graph based authorization library


## Overview

The permissions graph consists of Vertices and Edges.

**Vertices**

* `Resource`: a resource with predefined actions requiring authorization
* `User`: an identity that will take actions on resources
* `Group`: a named collection of `Users`

**Edges**

* `MemberOf`: indicates membership in a `UserGroup`.
    - `User -> MemberOf -> Group`
* `Allow`: indicates positive permission to act on a resource
    - `User -> Allow(action) -> Resource`
    - `Group -> Allow(action) -> Resource`
* `Deny`: indicates negative permission to act on a resource
    - `User -> Deny(action) -> Resource`
    - `Group -> Deny(action) -> Resource`

### Authorizing Access

Authorization to act on a resource is decided by finding the shortest path between
a user and the resource to be acted upon. If that shortest path is a positive
permission ("Allow"), the user is authorized. If that shortest path is a
negative permission ("Deny"), or if there is no path between
the user and the resource, the user is not authorized.

