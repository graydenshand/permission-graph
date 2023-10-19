import pytest

from permission_graph.structs import Action, Actor, Group, Resource, ResourceType


@pytest.fixture
def alice():
    return Actor(name="Alice")


@pytest.fixture
def admins():
    return Group(name="Admins")


@pytest.fixture()
def document_type():
    return ResourceType(name="Document", actions=["ViewDocument"])


@pytest.fixture()
def document():
    return Resource(name="My_Document.csv", resource_type="Document")


@pytest.fixture
def view_document():
    return Action(name="ViewDocument", resource_type="Document", resource="My_Document.csv")
