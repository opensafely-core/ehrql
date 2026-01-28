import datetime
import inspect
import re
from collections import defaultdict

from ehrql import tables
from ehrql.codes import BaseCode, BaseMultiCodeString
from ehrql.query_language import (
    EventFrame,
    PatientFrame,
    get_all_series_and_properties_from_class,
    get_tables_from_namespace,
)
from ehrql.utils.module_utils import get_submodules

from .common import (
    get_arguments,
    get_class_attrs,
    get_docstring,
    get_function_body,
    get_name_for_type,
)


SORT_ORDER = {k: i for i, k in enumerate(["tpp", "core"])}


def build_schemas(backends=()):
    module_name_to_backends = build_module_name_to_backend_map(backends)

    schemas = []
    for module in get_submodules(tables):
        module_tables = list(build_tables(module))
        if not module_tables:
            continue

        docstring = get_docstring(module)
        dotted_path = module.__name__
        hierarchy = dotted_path.removeprefix(f"{tables.__name__}.").split(".")
        name = ".".join(hierarchy)
        implemented_by = [
            backend_name for backend_name in module_name_to_backends[name]
        ]

        schemas.append(
            {
                "name": name,
                "dotted_path": dotted_path,
                "hierarchy": hierarchy,
                "docstring": docstring,
                "implemented_by": implemented_by,
                "is_raw": ".raw." in dotted_path,
                "tables": sorted(module_tables, key=lambda t: t["name"]),
            }
        )

    schemas.sort(key=sort_key)
    return schemas


def build_module_name_to_backend_map(backends):
    module_name_to_backends = defaultdict(list)
    for backend in backends:
        for module_name in backend["implements"]:
            module_name_to_backends[module_name].append(backend["name"])
    return module_name_to_backends


def build_tables(module):
    for table_name, table in get_tables_from_namespace(module):
        yield build_table(table_name, table)


def build_table(table_name, table):
    cls = table.__class__
    docstring = get_table_docstring(cls)
    required_permission = table._qm_node.required_permission
    has_one_row_per_patient = issubclass(cls, PatientFrame)
    activation_filter_field = table._qm_node.activation_filter_field

    columns = [
        build_column(
            table_name, column_name, series_or_property, has_one_row_per_patient
        )
        for column_name, series_or_property in get_all_series_and_properties_from_class(
            cls
        ).items()
    ]

    if required_permission:
        expected_string = f"`{required_permission}` permission"
        if expected_string not in docstring:
            raise ValueError(
                f"Table {cls!r} requires the {required_permission!r} permission "
                f"but doesn't include {expected_string!r} in its docstring"
            )

    if activation_filter_field is not False:
        expected_strings = ["activated GP practice"]
        if activation_filter_field is not None:
            expected_strings.append(f"`{activation_filter_field}`")
        if not all(string in docstring for string in expected_strings):
            extra_error_msg = (
                f" and the filter field {expected_strings[1]}"
                if activation_filter_field is not None
                else ""
            )
            raise ValueError(
                f"Table {cls!r} filters on GP activations but doesn't include {expected_strings[0]!r}{extra_error_msg} in its docstring"
            )

        # TODO: Remove this when GP activation filtering is live
        # Temporarily strip out the sentence referring to GP practice activation
        docstring = re.sub(
            r"By default[^\.]+activated GP practice[^\.]+are included\.",
            "",
            docstring,
            count=1,
            flags=re.DOTALL | re.MULTILINE,
        )

    return {
        "name": table_name,
        "docstring": docstring,
        "columns": columns,
        "has_one_row_per_patient": has_one_row_per_patient,
        "methods": build_table_methods(table_name, cls),
        "required_permission": required_permission,
    }


def build_column(table_name, column_name, series_or_property, has_one_row_per_patient):
    column_object = {
        "name": column_name,
    }
    if isinstance(series_or_property, property):
        type_ = inspect.signature(series_or_property.fget).return_annotation
        column_object["description"] = get_docstring(series_or_property)
        column_object["constraints"] = []
        column_object["source"] = re.sub(
            r"\bself\b", table_name, get_function_body(series_or_property.fget)
        )
    else:
        # Currently means it's a Series
        type_ = series_or_property.type_
        column_object["description"] = series_or_property.description
        column_object["constraints"] = [
            c.description for c in series_or_property.constraints
        ]

    column_object["type"] = get_name_for_type(type_)
    column_object["type_ref"] = get_ref_for_type(type_, has_one_row_per_patient)

    return column_object


def build_table_methods(table_name, cls):
    base_attrs = get_class_attrs(EventFrame).keys()
    return [
        build_method(table_name, name, attr)
        for name, attr in get_class_attrs(cls).items()
        if name not in base_attrs
        and not name.startswith("_")
        and inspect.isfunction(attr)
    ]


def build_method(table_name, name, method):
    return {
        "name": name,
        "docstring": get_docstring(method),
        "arguments": get_arguments(method, ignore_self=True),
        # Replace the `self` argument with the table name so the resulting code makes
        # more sense in isolation
        "source": re.sub(r"\bself\b", table_name, get_function_body(method)),
    }


def get_table_docstring(cls):
    docstring = get_docstring(cls, default="")
    # Check that inherited tables have consistent docstrings
    for parent in cls.__mro__:
        if parent is PatientFrame or parent is EventFrame:
            break
        parent_docstring = get_docstring(parent, default="")
        if not docstring.startswith(parent_docstring):
            raise ValueError(
                f"Table {cls!r} inherits from {parent!r} but does not match or "
                f"extend its docstring.\n"
                "\n"
                "Has one of the docstrings been edited and the other not updated?"
            )
    else:
        assert False  # Keep coverage happy
    return docstring


def get_ref_for_type(type_, has_one_row_per_patient):
    if issubclass(type_, BaseCode):
        ref = "Code"
    elif issubclass(type_, BaseMultiCodeString):
        ref = "MultiCodeString"
    elif issubclass(type_, bool | int | float | str | datetime.date):
        ref = type_.__name__.capitalize()
    else:
        assert False, f"Unknown: {type_}"
    suffix = "PatientSeries" if has_one_row_per_patient else "EventSeries"
    return f"{ref}{suffix}"


def sort_key(obj):
    k = obj["name"]
    return SORT_ORDER.get(k, float("+inf")), k
