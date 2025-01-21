import re
from enum import Enum
from pathlib import Path

import pytest

from ehrql import tables
from ehrql.query_language import (
    BaseSeries,
    get_tables_from_namespace,
)
from ehrql.query_model.nodes import SelectColumn
from ehrql.tables import core
from ehrql.utils.module_utils import get_submodules

from .language_server import LanguageServer


# Using the pyright language server to test ehrQL autocompletion
#


@pytest.fixture(scope="session")
def language_server(tmp_path_factory):
    temp_file_path = tmp_path_factory.mktemp("autoocomplete") / "autocomplete.py"
    return LanguageServer(temp_file_path)


class CompletionItemKind(Enum):
    """
    The different kinds of things the language server protocol supports.
    Currently we only have METHOD and VARIABLE but the full list is here:
    https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#completionItemKind
    """

    METHOD = 2
    VARIABLE = 6


base_frame_values = {
    "count_for_patient": CompletionItemKind.METHOD.value,
    "exists_for_patient": CompletionItemKind.METHOD.value,
}

event_frame_values = {
    **base_frame_values,
    "except_where": CompletionItemKind.METHOD.value,
    "sort_by": CompletionItemKind.METHOD.value,
    "where": CompletionItemKind.METHOD.value,
}


@pytest.mark.parametrize(
    "table, expected_values",
    [
        (
            core.patients,
            {
                **base_frame_values,
                "age_on": CompletionItemKind.METHOD.value,
                "date_of_birth": CompletionItemKind.VARIABLE.value,
                "date_of_death": CompletionItemKind.VARIABLE.value,
                "is_alive_on": CompletionItemKind.METHOD.value,
                "is_dead_on": CompletionItemKind.METHOD.value,
                "sex": CompletionItemKind.VARIABLE.value,
            },
        ),
        (
            core.clinical_events,
            {
                **event_frame_values,
                "date": CompletionItemKind.VARIABLE.value,
                "numeric_value": CompletionItemKind.VARIABLE.value,
                "snomedct_code": CompletionItemKind.VARIABLE.value,
            },
        ),
        (
            core.practice_registrations,
            {
                **event_frame_values,
                "end_date": CompletionItemKind.VARIABLE.value,
                "exists_for_patient_on": CompletionItemKind.METHOD.value,
                "for_patient_on": CompletionItemKind.METHOD.value,
                "practice_pseudo_id": CompletionItemKind.VARIABLE.value,
                "spanning": CompletionItemKind.METHOD.value,
                "start_date": CompletionItemKind.VARIABLE.value,
            },
        ),
        (
            core.ons_deaths,
            {
                **base_frame_values,
                "cause_of_death_01": CompletionItemKind.VARIABLE.value,
                "cause_of_death_02": CompletionItemKind.VARIABLE.value,
                "cause_of_death_03": CompletionItemKind.VARIABLE.value,
                "cause_of_death_04": CompletionItemKind.VARIABLE.value,
                "cause_of_death_05": CompletionItemKind.VARIABLE.value,
                "cause_of_death_06": CompletionItemKind.VARIABLE.value,
                "cause_of_death_07": CompletionItemKind.VARIABLE.value,
                "cause_of_death_08": CompletionItemKind.VARIABLE.value,
                "cause_of_death_09": CompletionItemKind.VARIABLE.value,
                "cause_of_death_10": CompletionItemKind.VARIABLE.value,
                "cause_of_death_11": CompletionItemKind.VARIABLE.value,
                "cause_of_death_12": CompletionItemKind.VARIABLE.value,
                "cause_of_death_13": CompletionItemKind.VARIABLE.value,
                "cause_of_death_14": CompletionItemKind.VARIABLE.value,
                "cause_of_death_15": CompletionItemKind.VARIABLE.value,
                "cause_of_death_is_in": CompletionItemKind.METHOD.value,
                "date": CompletionItemKind.VARIABLE.value,
                "underlying_cause_of_death": CompletionItemKind.VARIABLE.value,
            },
        ),
        (
            core.medications,
            {
                **event_frame_values,
                "date": CompletionItemKind.VARIABLE.value,
                "dmd_code": CompletionItemKind.VARIABLE.value,
            },
        ),
    ],
)
def test_core_tables(language_server, table, expected_values):
    # Check the autocompletion for each core table. I.e.
    # what you get after typing: patients.

    table_name = f"ehrql.tables.core.{table.__class__.__name__}"

    results = language_server.get_completion_results(
        f"import ehrql.tables.core; {table_name}."
    )

    actual = {}
    for x in results:
        if not x.get("label").startswith("_"):
            actual[x.get("label")] = x.get("kind")

    assert actual == expected_values


def test_core_table_tests_are_exhaustive():
    # Checking that the parameters to the previous test
    # include all current core tables
    params = test_core_tables.pytestmark[0].args[1]
    tables = [arg[0] for arg in params]
    missing = [
        name for name, table in get_tables_from_namespace(core) if table not in tables
    ]

    assert not missing, f"No tests for core tables: {', '.join(missing)}"


# If we create a file once, with many lines of code, which the language
# server can then load and parse, then the autocomplete is a lot quicker
# than continually telling the language server about a line changing.
# Therefore for the parameterized tests, we first populate a file with
# all statements.
import_statements = [f"import {module.__name__}" for module in get_submodules(tables)]
all_columns_for_all_tables = [
    (
        f"{module.__name__}.{name}.{column_name}",
        module,
        name,
        column_name,
        type(getattr(table, column_name)).__name__,
    )
    for module in get_submodules(tables)
    for name, table in get_tables_from_namespace(module)
    for column_name in dir(table)
    if isinstance(getattr(table, column_name), BaseSeries)
    and isinstance(getattr(table, column_name)._qm_node, SelectColumn)
]


@pytest.fixture(scope="session")
def language_server_preloaded_with_all_types(language_server, tmp_path_factory):
    temp_file_path = tmp_path_factory.mktemp("autoocomplete") / "autocomplete.py"
    content = [thing[0] for thing in all_columns_for_all_tables]
    language_server.open_doc(temp_file_path, "\n".join(import_statements + content))
    return language_server


@pytest.mark.parametrize(
    "line, code_string, module, name, column_name, expected_series_type",
    [
        (line, code_string, module, name, column_name, expected_series_type)
        for line, (
            code_string,
            module,
            name,
            column_name,
            expected_series_type,
        ) in enumerate(all_columns_for_all_tables)
    ],
)
def test_types(
    language_server_preloaded_with_all_types,
    line,
    code_string,
    module,
    name,
    column_name,
    expected_series_type,
):
    # For each Series on each table in each submodule of ehrql.tables we check
    # that the inferred series type on hovering matches the expected series
    result = language_server_preloaded_with_all_types.get_element_type_from_file(
        line + len(import_statements), len(code_string) - 1
    )
    assert expected_series_type == result, (
        f"In {module.__name__}.{name}, the series `{column_name}` should be of type `{expected_series_type}` but the language server thinks it's `{result}`"
    )


def get_lines_and_expected_types_from_autocomplete_def_file():
    autocomplete_filepath = Path(__file__).with_name("autocomplete_definition.py")
    autocomplete_file = autocomplete_filepath.read_text()
    lines = autocomplete_file.split("\n")
    lines_with_expected_type = []
    multiline_variable_name = None
    multiline_optional_method = None
    multiline_statement_lines = []
    multiline_line_number = None
    is_multiline_statement = False
    for idx, line in enumerate(lines):
        line_number = idx + 1

        # To match lines like:
        #   var_name = some.statement.following.variable.assignment  ## type: TypeSeries
        single_line_assignment = re.search(
            "^(?P<var_name>.+) = (?P<statement>.+)  ## type:(?P<expected_type>.+)$",
            line,
        )

        # To match lines like:
        #   statement.calls.method(some, props)  ## type: TypeSeries
        single_line_method_call = re.search(
            "^(?P<obj>.+)\\.(?P<method>[^.(]+\\(.*\\))  ## type:(?P<expected_type>.+)$",
            line,
        )

        # To match lines like:
        #   some.statement.without.variable.assignment  ## type: TypeSeries
        statement_with_expected_type = re.search(
            "^(?P<statement>.+)  ## type:(?P<expected_type>.+)$", line
        )

        # To match lines like:
        #   var_name = (
        # i.e. things that are the start of a multiline assigment
        # Can optionally be a method call like:
        #   var_name = method_with_many_params(
        start_of_multiline_statement = re.search(
            "^(?P<var_name>[A-Za-z0-0_]+) = (?P<optional_method>.*)\\($", line
        )

        # To match lines like:
        #   )  ## type:TypeSeries
        # i.e. the end of a multiline statement
        end_of_multiline_statement = re.search(
            "^\\)  ## type:(?P<expected_type>.+)$", line
        )
        if line.startswith("from") or line.startswith("import"):
            # import statement, ignore
            ...
        elif (
            line.strip() == ""
            or line.strip().startswith("#")
            or line.strip().startswith("date_str = ")
        ):
            # empty line or comment so ignore
            # also ignore the helper var date_str
            ...
        elif end_of_multiline_statement:
            is_multiline_statement = False
            assert len(multiline_statement_lines) > 0, (
                f"I couldn't parse the multiline variable assigment for variable: {multiline_variable_name}"
            )
            statement = f"{multiline_variable_name}={multiline_optional_method}({''.join(multiline_statement_lines)});{multiline_variable_name}"
            multiline_optional_method = False
            expected_type = end_of_multiline_statement.group("expected_type").strip()
            lines_with_expected_type.append(
                (statement, multiline_line_number, 0, expected_type)
            )
        elif is_multiline_statement:
            multiline_statement_lines.append(line.split("#")[0].strip())
        elif single_line_assignment:
            statement = (
                single_line_assignment.group("var_name").strip()
                + "="
                + single_line_assignment.group("statement").strip()
            )
            expected_type = single_line_assignment.group("expected_type").strip()

            # The line is a variable assigment, so hovering over the first character
            # in the line brings up the type of the variable.
            cursor_position = 0
            lines_with_expected_type.append(
                (statement, line_number, cursor_position, expected_type)
            )
        elif single_line_method_call:
            obj = single_line_method_call.group("obj").strip()
            method = single_line_method_call.group("method").strip()
            statement = f"{obj}.{method}"

            expected_type = single_line_method_call.group("expected_type").strip()

            # For a method call, the cursor position to hover is somewhere over the
            # method name. The matching above finds the object that the method is
            # called on. 1 character after that is the '.' and 2 characters after
            # is the start of the method name
            cursor_position = len(obj) + 2
            lines_with_expected_type.append(
                (statement, line_number, cursor_position, expected_type)
            )
        elif statement_with_expected_type:
            statement = statement_with_expected_type.group("statement").strip()
            expected_type = statement_with_expected_type.group("expected_type").strip()

            # For a non-method statement, the last thing is the property/attribute
            # that we want the type for, so the cursor position can be the end of
            # the line
            cursor_position = len(statement)
            lines_with_expected_type.append(
                (statement, line_number, cursor_position, expected_type)
            )
        elif start_of_multiline_statement:
            multiline_variable_name = start_of_multiline_statement.group("var_name")
            multiline_line_number = line_number
            is_multiline_statement = True
            multiline_statement_lines = []
            multiline_optional_method = start_of_multiline_statement.group(
                "optional_method"
            )
        else:  # pragma: no cover
            assert 0, (
                f"The autocomplete_definition.py file contains an unexpected line: [{line}]\n\n"
                "All lines must either be:\n"
                " - An import statement\n"
                " - A comment\n"
                " - of the format: <expression_to_evaluate> ## type:<expected_type>\n"
            )
    assert not is_multiline_statement, (
        f"There is a multiline variable assignment for {multiline_variable_name}"
    )
    ", which doesn't end. Multiline variable assigments"
    return lines_with_expected_type


@pytest.fixture(scope="session")
def language_server_preloaded_with_autocomplete_defs(language_server, tmp_path_factory):
    temp_file_path = tmp_path_factory.mktemp("autoocomplete") / "autocomplete.py"

    autocomplete_filepath = Path(__file__).with_name("autocomplete_definition.py")
    content = autocomplete_filepath.read_text()

    language_server.open_doc(temp_file_path, content)
    return language_server


@pytest.mark.parametrize(
    "statement, line_number, cursor_position, expected_type",
    get_lines_and_expected_types_from_autocomplete_def_file(),
)
def test_things_in_autocomplete_definition_file(
    language_server_preloaded_with_autocomplete_defs,
    statement,
    line_number,
    cursor_position,
    expected_type,
):
    actual_type = (
        language_server_preloaded_with_autocomplete_defs.get_element_type_from_file(
            line_number - 1, cursor_position
        )
    )
    assert actual_type == expected_type, (
        f"\n\nautocomplete_definition.py, line {line_number}: Expecting {expected_type} (but got {actual_type}) for the statement\n{statement}\n"
    )
