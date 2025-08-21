"""
Provides a simple mechanism for registering query model objects so that they can
serialized by reference, rather than by serializing the entire object structure.
"""


class RegistryError(Exception):
    pass


REGISTRY_OBJ_TO_ID = {}
REGISTRY_ID_TO_OBJ = {}


def register_object(obj, module, name):
    obj_id = (module, name)
    if obj_id in REGISTRY_ID_TO_OBJ:
        if REGISTRY_ID_TO_OBJ[obj_id] != obj:
            raise RegistryError("Distinct object already registered with ID: {obj_id}")
    REGISTRY_OBJ_TO_ID[obj] = obj_id
    REGISTRY_ID_TO_OBJ[obj_id] = obj


def get_id_for_object(obj):
    try:
        return REGISTRY_OBJ_TO_ID[obj]
    except KeyError:
        raise RegistryError("Object has not been registered: {obj}")


def get_object_by_id(obj_id):
    try:
        return REGISTRY_ID_TO_OBJ[obj_id]
    except KeyError:
        raise RegistryError(f"No object registered with ID: {obj_id}")
