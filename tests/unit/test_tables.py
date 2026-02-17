import inspect
import re

import pytest

import ehrql.backends
import ehrql.tables
from ehrql.query_language import get_tables_from_namespace
from ehrql.tables import Constraint, tpp
from ehrql.utils.module_utils import get_submodules


@pytest.mark.parametrize("module", list(get_submodules(ehrql.tables)))
def test___all__(module):
    table_names = {name for name, _ in get_tables_from_namespace(module)}
    if not table_names:
        pytest.skip(f"{module.__name__} has no tables")
    assert module.__all__ == sorted(module.__all__)
    assert table_names == set(module.__all__)


ACTIVATION_FILTERED_BACKENDS = ["TPPBackend"]


def get_backends():
    """
    Yield all ehrQL backend classes that inherit from BaseBackend and
    implement tables
    """
    for namespace in get_submodules(ehrql.backends):
        for attr, value in vars(namespace).items():
            if inspect.isclass(value) and getattr(value, "implements", None):
                yield attr, value


@pytest.mark.parametrize("backend_name, backend_class", list(get_backends()))
def test_backend_tables_configure_activation_filtering_if_required(
    backend_name, backend_class
):
    if backend_name not in ACTIVATION_FILTERED_BACKENDS:
        pytest.skip(f"backend {backend_name} does not require activation filtering")
    for module in backend_class.implements:
        for name, table in get_tables_from_namespace(module):
            meta = getattr(table, "_meta", None)
            assert hasattr(meta, "activation_filter_field"), (
                f"{module.__name__}.{name} must configure GP activation filtering by specifying `activation_filter_field` in its _meta subclass"
            )


@pytest.mark.parametrize("backend_name, backend_class", list(get_backends()))
def test_backend_tables_defined_as_public_or_internal(backend_name, backend_class):
    """
    Every table defined on a Backend must either be exposed in the user-facing
    public tables, or defined in the backend's internal_tables. This ensures all
    backend tables are properly tested in the integration tests.
    """
    public_tables = set()
    for module in backend_class.implements:
        for name, table in get_tables_from_namespace(module):
            meta = getattr(table, "_meta", None)
            public_tables.add(getattr(meta, "table_name", name))
    internal_tables = set(backend_class.internal_tables)
    assert public_tables | internal_tables == set(backend_class.tables)


valid_examples_for_regex_constraints = [
    (tpp.addresses, "msoa_code", "E02012345"),
    (tpp.ec, "sus_hrg_code", "AA00A"),
    (tpp.opa, "hrg_code", "AA00A"),
    (tpp.practice_registrations, "practice_stp", "E54000012"),
    (tpp.wl_clockstops, "activity_treatment_function_code", "AB1"),
    (tpp.wl_openpathways, "activity_treatment_function_code", "AB1"),
    (tpp.wl_openpathways, "source_of_referral", "A1"),
]

invalid_examples_for_regex_constraints = [
    (tpp.addresses, "msoa_code", "X02012345"),
    (tpp.ec, "sus_hrg_code", "AA000A"),
    (tpp.opa, "hrg_code", "AA000A"),
    (tpp.practice_registrations, "practice_stp", "X54000012"),
    (tpp.wl_clockstops, "activity_treatment_function_code", "AB10"),
    (tpp.wl_openpathways, "activity_treatment_function_code", "AB10"),
    (tpp.wl_openpathways, "source_of_referral", "A10"),
]


@pytest.mark.parametrize(
    "table,column_name,example", valid_examples_for_regex_constraints
)
def test_regex_constraints_match_valid_examples(table, column_name, example):
    regex = get_regex_constraint(table, column_name)
    assert bool(re.fullmatch(regex, example))


@pytest.mark.parametrize(
    "table,column_name,example", invalid_examples_for_regex_constraints
)
def test_regex_constraints_do_not_match_invalid_examples(table, column_name, example):
    regex = get_regex_constraint(table, column_name)
    assert not bool(re.fullmatch(regex, example))


@pytest.mark.parametrize(
    "examples",
    [valid_examples_for_regex_constraints, invalid_examples_for_regex_constraints],
)
def test_all_regex_constraints_are_tested(examples):
    tables = {
        table
        for module in get_submodules(ehrql.tables)
        for _, table in get_tables_from_namespace(module)
    }
    tables_column_names = {
        (table, column_name)
        for table in tables
        for column_name in table._qm_node.schema.column_names
        if get_regex_constraint(table, column_name)
    }

    assert tables_column_names == {
        (table, column_name) for table, column_name, _ in examples
    }


def get_regex_constraint(table, column_name):
    schema = table._qm_node.schema
    constraint = schema.get_column_constraint_by_type(column_name, Constraint.Regex)
    return getattr(constraint, "regex", None)
