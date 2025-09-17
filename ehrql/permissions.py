import json

from ehrql.query_model.introspection import get_table_nodes
from ehrql.serializer_registry import RegistryError, get_id_for_object


class EHRQLPermissionError(Exception):
    pass


def enforce_permissions(dataset, environ):
    available_permissions = parse_permissions(environ)
    required_permissions = get_required_permissions(dataset)
    missing_permissions = {
        k: v for k, v in required_permissions.items() if k not in available_permissions
    }
    if missing_permissions:
        raise EHRQLPermissionError(
            f"You do not currently have all the permissions needed for this action.\n"
            f"\n"
            f"Missing permissions are:\n"
            f"\n"
            f"{format_permission_list(missing_permissions)}\n"
            f"\n"
            f"If you think this is a mistake and that you should have these "
            f"permissions please contact OpenSAFELY support."
        )


def parse_permissions(environ):
    permissions_str = environ.get("EHRQL_PERMISSIONS") or "[]"
    return set(json.loads(permissions_str))


def get_required_permissions(dataset):
    table_permissions = {}
    for table in get_table_nodes(dataset):
        if perm := table.required_permission:
            table_permissions.setdefault(perm, []).append(table)

    required_permissions = {}
    for permission, tables in table_permissions.items():
        required_permissions[permission] = (
            f"required for access to the {format_table_list(tables)}"
        )

    return required_permissions


def format_permission_list(missing_permissions):
    return "\n".join(
        f"    * {name}: {description}"
        for name, description in missing_permissions.items()
    )


def format_table_list(tables):
    names = [f"`{get_public_name_for_table(table)}`" for table in tables]
    if len(names) == 1:
        return f"{names[0]} table"
    elif len(tables) > 1:
        return f"{', '.join(names[:-1])} and {names[-1]} tables"
    else:
        assert False


def get_public_name_for_table(table):
    # To provide the table reference in the most helpful form to the user we rely on the
    # registry to tell us the module and name under which it was defined.
    try:
        module, name = get_id_for_object(table)
        return f"{module}.{name}".removeprefix("ehrql.tables.")
    except RegistryError:
        # If for some reason, which shouldn't occur under normal usage, we've got a
        # table that hasn't been preregistered that just use its name in the query
        # model rather than failing entirely.
        return table.name
