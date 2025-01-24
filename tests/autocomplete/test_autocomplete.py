import ast
import re
from enum import Enum
from io import BytesIO
from pathlib import Path
from tokenize import tokenize

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

# Before we run the tests we first parse the autocomplete_definition.py file
# to pull out:
#   - all statements (either methods or direct attribute references)
#   - all assignments
#   - the expected type for each, parsed from the structured comments
#   - the line number and cursor position to hover to get the expected type

autocomplete_filepath = Path(__file__).with_name("autocomplete_definition.py")
autocomplete_file = autocomplete_filepath.read_text()

# We want to ensure that all lines in the autocomplete file are covered by tests
# so we keep track of those that aren't
autocomplete_uncovered_lines = set(range(0, len(autocomplete_file.split("\n")) + 1))

# Using the tokenize method we can parse all tokens, including comments, to
# find the structured comments containing the expected types. For each we
# record the line number that it occurs on, and the expected type.
expected_types = {}
for token_type, string, start, end, line in tokenize(
    BytesIO(autocomplete_file.encode("utf-8")).readline
):
    if (
        line.strip() == ""
        or line.strip().startswith("#")
        or line.strip().startswith("from")
        or line.strip().startswith("import")
    ):
        # Comments and import statements can be ignored
        autocomplete_uncovered_lines.discard(start[0])
    type_comment = re.search("^## type:(?P<expected_type>.+)$", string)
    if type_comment:
        expected_types[start[0]] = type_comment.group("expected_type").strip()


# Now we use the AST module to walk the trees in the autocomplete file. This
# allows us to:
#   - find all statements and assignments
#   - for all methods find the method name and the calling object
#   - find the line_number and cursor_position for where to hover
#   - find the line_number where we expect to see a structured comment with the
#     expected type
class MyVisitor(ast.NodeVisitor):
    """
    Traverst the AST to find all the method calls along
    with the object they were called from
    """

    def __init__(self):
        self.statements = []

    def update_coverage(self, node):
        for line_number in range(node.lineno, node.end_lineno + 1):
            autocomplete_uncovered_lines.discard(line_number)

    def get_expected_type(self, line_number, statement):
        if line_number not in expected_types:  # pragma: no cover
            assert 0, (
                f"Line {line_number} of the autocomplete_definition.py file does not "
                "have an expected type in a structured comment. You need to provide a "
                "comment like `## type:<expected_type>` immediately after the statement.\n"
                "If this is a multi line statement, then put it on the last line. Typically "
                "this will be immediately after the closing ')'.\n"
                "The statement without an expression is:\n\n"
                f"{statement}\n"
            )
        return expected_types[line_number]

    def process_attribute(
        self, line_number, expected_type_line, statement, cursor_position
    ):
        expected_type = self.get_expected_type(expected_type_line, statement)
        self.statements.append((statement, line_number, cursor_position, expected_type))

    def visit_Attribute(self, node):
        # Occurs when a statement is just an attribute call without assignment
        # e.g. patients.core.date_of_birth
        self.update_coverage(node)
        self.process_attribute(
            node.end_lineno, node.end_lineno, ast.unparse(node), node.end_col_offset
        )

    def visit(self, node):
        if not isinstance(
            node,
            ast.Module  # always first node, we ignore
            | ast.ImportFrom  # ignore import statements
            | ast.alias  # ignore alias statements
            | ast.Expr  # everything is an expression, we ignore because we are only interested in the expression type
            | ast.Assign  # dealt with by visit_Assign
            | ast.Attribute  # dealt with by visit_Attribute
            | ast.Call,  # dealt with by visit_Call
        ):  # pragma: no cover
            assert 0, (
                f"Line {node.lineno} of autocomplete.definition.py contains an unexpected expression "
                "and so won't be tested. See the comments in that file for what is a valid expression. "
                "If you need to test the expression, then you will need to update this test file. The "
                f"unexpected expression was:\n\n{ast.unparse(node)}\n"
            )
        return super().visit(node)

    def process_function(self, node, statement, cursor_position):
        expected_type = self.get_expected_type(node.end_lineno, statement)
        line_number = node.func.end_lineno
        self.statements.append((statement, line_number, cursor_position, expected_type))

    def visit_Call(self, node):
        # Occurs when a statement is just a method call without assignment
        # e.g. patients.core.date_of_birth.is_after("2024-01-01")
        self.update_coverage(node)
        self.process_function(node, ast.unparse(node), node.func.end_col_offset)

    def visit_Assign(self, node):
        # Occurs when a statement is an assignment
        # e.g. var_name = patients.core.date_of_birth.is_after("2024-01-01")
        # We process the statement assigned to the variable

        if node.targets[0].id == "date_str":
            # Ignore the line that just defines a variable `date_str`
            self.update_coverage(node)
            return

        if isinstance(node.value, ast.Attribute):  # pragma: no cover
            # Currently we don't actually do this, hence the pragma, but leaving
            # it in so that potential future changes to the autocomplete_definition
            # file can be handled
            self.update_coverage(node)
            self.process_attribute(node.lineno, node.end_lineno, ast.unparse(node), 0)
        elif isinstance(node.value, ast.Call):
            self.update_coverage(node)
            self.process_function(node.value, ast.unparse(node), 0)
        else:
            # Sometimes we may want to test autocomplete for something that isn't
            # an attribute or a method call. In which case this is fine with a variable
            # assignment because the autocomplete can come from a hover at cursor
            # position 0 (the start of the variable name)
            self.update_coverage(node)
            statement = ast.unparse(node.value)
            expected_type = self.get_expected_type(node.end_lineno, statement)
            self.statements.append((statement, node.lineno, 0, expected_type))


visitor = MyVisitor()
visitor.visit(ast.parse(autocomplete_file))
autocomplete_file_statements = visitor.statements

assert len(autocomplete_uncovered_lines) == 0, (
    "The autocomplete_definition.py contains some lines that aren't covered by the tests:\n"
    f"{autocomplete_uncovered_lines}\n"
    "You have probably added something to it that the AST NodeVisitor isn't expecting."
)


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


@pytest.fixture(scope="session")
def language_server_preloaded_with_autocomplete_defs(language_server, tmp_path_factory):
    temp_file_path = tmp_path_factory.mktemp("autoocomplete") / "autocomplete.py"
    language_server.open_doc(temp_file_path, autocomplete_file)
    return language_server


@pytest.mark.parametrize(
    "statement, line_number, cursor_position, expected_type",
    autocomplete_file_statements,
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
