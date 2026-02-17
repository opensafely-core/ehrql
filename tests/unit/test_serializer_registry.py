import pytest

from ehrql import serializer_registry
from ehrql.query_model.nodes import Value


def test_register_object():
    node = Value(123)
    serializer_registry.register_object(node, __name__, "test_register_object_1")
    # Registering the same value again under the same name is fine
    serializer_registry.register_object(node, __name__, "test_register_object_1")
    # As is registering the same value under a different name
    serializer_registry.register_object(node, __name__, "test_register_object_1_again")
    # But registering a different object under the same name is an error
    node_2 = Value(456)
    with pytest.raises(
        serializer_registry.RegistryError, match="object already registered with ID"
    ):
        serializer_registry.register_object(node_2, __name__, "test_register_object_1")


def test_roundtrip():
    node = Value(789)
    serializer_registry.register_object(node, __name__, "test_roundtrip")
    obj_id = serializer_registry.get_id_for_object(node)
    obj = serializer_registry.get_object_by_id(obj_id)
    assert obj is node


def test_get_id_for_object_error():
    with pytest.raises(
        serializer_registry.RegistryError, match="Object has not been registered"
    ):
        serializer_registry.get_id_for_object(Value("hello"))


def test_get_object_by_id_error():
    with pytest.raises(
        serializer_registry.RegistryError, match="No object registered with ID"
    ):
        serializer_registry.get_object_by_id((__name__, "missing_object"))
