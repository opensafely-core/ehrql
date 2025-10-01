import json
import logging

from ehrql.query_model import nodes as qm
from ehrql.query_model.introspection import get_table_nodes
from ehrql.serializer_registry import RegistryError, get_id_for_object
from ehrql.utils.log_utils import indent


log = logging.getLogger()


CLAIMED_PERMISSIONS = {}


class EHRQLPermissionError(Exception):
    pass


def claim_permissions(*permissions):
    """
    This function allows you to access any restricted table or feature when working with
    dummy data. It will NOT allow you access with real data: for that you will need the
    appropriate permissions on the OpenSAFELY platform.

    Permission names are strings and should be written with double quotes e.g.

        from ehrql import claim_permissions

        claim_permissions("some_permission", "another_permission")

    This can go anywhere in your dataset or measure definition file.

    You can make multiple `claim_permissions()` calls and the permissions will be
    combined together.
    """
    for permission in permissions:
        # Use dictionary as convenient ordered set
        CLAIMED_PERMISSIONS[permission] = True


def clear_claimed_permissions():
    CLAIMED_PERMISSIONS.clear()


def get_claimed_permissions():
    return tuple(CLAIMED_PERMISSIONS.keys())


def enforce_permissions(dataset, environ):
    available_permissions = parse_permissions(environ)
    missing_permissions = get_missing_permissions(dataset, available_permissions)
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


def enforce_permissions_for_dummy_data(dataset, claimed_permissions):
    missing_permissions = get_missing_permissions(dataset, claimed_permissions)
    if missing_permissions:
        claim_list = ", ".join(
            f'"{p}"' for p in [*claimed_permissions, *missing_permissions]
        )
        message = (
            f"Some of the tables or features you are using require special permission to use with real\n"
            f"patient data. The permissions needed are:\n"
            f"\n"
            f"{format_permission_list(missing_permissions)}\n"
            f"\n"
            f"You can continue to work on your code using dummy data by “claiming” "
            f"the required permisions:\n"
            f"\n"
            f"    from ehrql import claim_permissions\n"
            f"    claim_permissions({claim_list})\n"
            f"\n"
            f"Note that you will only be able to run your code against real data if you actually have these\n"
            f"permissions assigned by the OpenSAFELY team. For more information see:\n"
            f"https://docs.opensafely.org/ehrql/reference/language/#permissions"
        )
        # For the initial rollout of this feature we issue a warning locally but
        # continue running. Eventually we want to make this a hard error so that it
        # can't be missed.
        log.warning(indent(message))


def parse_permissions(environ):
    permissions_str = environ.get("EHRQL_PERMISSIONS") or "[]"
    return set(json.loads(permissions_str))


def get_missing_permissions(dataset, available_permissions):
    required_permissions = get_required_permissions(dataset)
    return {
        k: v for k, v in required_permissions.items() if k not in available_permissions
    }


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

    if isinstance(dataset, qm.Dataset) and dataset.events:
        required_permissions["event_level_data"] = (
            "required in order to use the `dataset.add_event_table()` method"
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
