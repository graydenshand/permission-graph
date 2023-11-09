from permission_graph.structs import Action, Actor, Group, Resource, ResourceType

ALICE = Actor(name="Alice")
ADMINS = Group(name="Admins")
DOCUMENT_TYPE = ResourceType(name="Document", actions=["ViewDocument"])
DOCUMENT = Resource(name="My_Document.csv", resource_type="Document")
VIEW_DOCUMENT = Action(name="ViewDocument", resource_type="Document", resource="My_Document.csv")
