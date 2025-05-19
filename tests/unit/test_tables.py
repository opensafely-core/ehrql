import re

import pytest

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


valid_examples_for_regex_constraints = [
    (tpp.addresses, "msoa_code", "E02012345"),
    (tpp.ec, "sus_hrg_code", "AA00A"),
    (tpp.opa, "hrg_code", "AA00A"),
    (tpp.opa, "provider_code", "ABC"),
    (tpp.opa, "provider_code", "89999"),
    (tpp.opa, "provider_code", "ABC01"),
    (tpp.practice_registrations, "practice_stp", "E54000012"),
    (tpp.wl_clockstops, "activity_treatment_function_code", "AB1"),
    (tpp.wl_openpathways, "activity_treatment_function_code", "AB1"),
    (tpp.wl_openpathways, "source_of_referral", "A1"),
]

invalid_examples_for_regex_constraints = [
    (tpp.addresses, "msoa_code", "X02012345"),
    (tpp.ec, "sus_hrg_code", "AA000A"),
    (tpp.opa, "hrg_code", "AA000A"),
    (tpp.opa, "provider_code", "AB"),
    (tpp.opa, "provider_code", "123456"),
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
