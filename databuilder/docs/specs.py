import inspect
import re
from importlib import import_module


def build_specs():
    """Return data describing the specs for use in documentation.

    The structure is derived from tests.spec.toc:
      * the specs are organised into chapters, with one chapter per test package
      * each chapter is split into sections, with one section per test module
      * each section is split into paragraphs, with one paragraph per test function
    """
    toc = import_module("tests.spec.toc")
    return [
        build_chapter(str(ix + 1), package_name, module_names)
        for ix, (package_name, module_names) in enumerate(toc.contents.items())
    ]


def build_chapter(chapter_id, package_name, module_names):
    """Return dict containing details of a single chapter.

    There is a section for each test package.
    """

    package = import_module(f"tests.spec.{package_name}")
    text = getattr(package, "text", None)
    return concatenate_optional_text(
        {
            "id": chapter_id,
            "title": package.title,
            "sections": [
                build_section(f"{chapter_id}.{ix + 1}", package_name, module_name)
                for ix, module_name in enumerate(module_names)
            ],
        },
        text,
    )


def build_section(section_id, package_name, module_name):
    """Return dict containing details of a single section.

    There is a section for each test module.
    """

    module = import_module(f"tests.spec.{package_name}.{module_name}")
    test_fns = [v for k, v in vars(module).items() if k.startswith("test_")]
    paragraphs = [
        build_paragraph(f"{section_id}.{ix + 1}", test_fn)
        for ix, test_fn in enumerate(test_fns)
    ]
    text = getattr(module, "text", None)
    return concatenate_optional_text(
        {
            "id": section_id,
            "title": module.title,
            "paragraphs": paragraphs,
        },
        text,
    )


def get_title_for_test_fn(test_fn):
    if hasattr(test_fn, "title"):
        return test_fn.title
    return test_fn.__name__.removeprefix("test_").replace("_", " ").capitalize()


def build_paragraph(paragraph_id, test_fn):
    """Return dict containing details of a single paragraph.

    There is a paragraph for each test function.
    """

    title = get_title_for_test_fn(test_fn)

    # Capture the arguments that the test function is called with.
    capturer = ArgCapturer()
    test_fn(capturer)

    # Retrieve and process the captured arguments.
    tables = {
        get_table_name(table): parse_table(s)
        for table, s in capturer.table_data.items()
    }
    output = [
        [str(patient_id), str(convert_output_value(value))]
        for patient_id, value in capturer.expected_output.items()
    ]

    # Get the source of the test function.
    source_lines = inspect.getsource(test_fn).splitlines()

    # Find the line the source where spec_test is called.
    ix = source_lines.index("    spec_test(")

    # Check that the next line is as expected.
    assert source_lines[ix + 1] == "        table_data,"

    series = get_series_code(source_lines, ix + 2, capturer.set_population)

    # Extract descriptive docstring if any
    text = inspect.getdoc(test_fn)

    return concatenate_optional_text(
        {
            "id": paragraph_id,
            "title": title,
            "tables": tables,
            "series": series,
            "output": output,
        },
        text,
    )


def get_series_code(source_lines, series_index, set_population=False):
    """
    Extract the definition of the series from the test function.
    """
    # A series may be defined over more than one line; iterate over the next
    # lines and build the string representing the series definition; when a potential
    # ending (a , at the end of a line) is found, check that the parentheses in the
    # statement so far are balanced; if they are not, we haven't reached the end of the
    # definition yet.
    first_series_line = source_lines[series_index]
    # Find the leading whitespace for the first line; this will be stripped, but in order to
    # preserve indentation, we strip only the equivalent whitespace from any subsequent lines.
    leading_whitespace_match = re.match(r"^(?P<whitespace>\s+)\w*", first_series_line)
    if leading_whitespace_match:
        leading_whitespace = leading_whitespace_match.group("whitespace")
    else:
        leading_whitespace = ""
    series_lines = []
    for line in source_lines[series_index:]:
        series_lines.append(line.rstrip().replace(leading_whitespace, ""))
        series_line = "".join(series_lines)
        if series_line.strip().endswith(","):
            # check series_line is balanced; if it is, then we're done
            if series_is_balanced(series_line):
                break
    series = "\n".join(series_lines).strip().removesuffix(",")

    if set_population:
        # If this test set a custom population, we need to parse the rest of the lines for
        # the population definition
        population_lines = []
        for line in source_lines[series_index:]:
            if population_lines or line.strip().startswith("population="):
                formatted_line = (
                    line.rstrip()
                    .replace("population=", "")
                    .replace(leading_whitespace, "")
                )
                population_lines.append(formatted_line)
                population_line = "".join(population_lines)

                # check population_line is balanced; if it is, then we're done
                if series_is_balanced(population_line):
                    break
        if len(population_lines) > 1:
            indent = " " * 4
            population = f"\n{indent}".join(population_lines).strip().removesuffix(",")
            population = f"set_population(\n{indent}{population}\n)"
        else:
            population = (
                f"set_population({population_lines[0].strip().removesuffix(',')})"
            )
        series = f"{series}\n{population}"
    return series


def series_is_balanced(series_line_string):
    """
    Takes a string representing a series definition and ensures that parentheses are
    balanced.
    """
    stack = []
    for char in series_line_string:
        if char == "(":
            stack.append(char)
        elif char == ")":
            # we can assume that the string composing a series definition will always be valid
            # syntax, but may not be complete yet.  If we encounter a closing parenthesis, the
            # last item on the stack must always be an opening parenthesis
            assert stack[-1] == "("
            stack.pop()
    return len(stack) == 0


def concatenate_optional_text(dictionary, text):
    return dictionary | {"text": text} if text else dictionary


def get_table_name(table):
    """Given a QL table, return the name of the variable that refers to the table in
    tests.spec.tables.

    This is the name that will have been used in the specs.
    """

    return {
        "patient_level_table": "p",
        "event_level_table": "e",
    }[table.qm_node.name]


def parse_table(s):
    """Return data in table as list of lists."""

    header, _, *rows = s.strip().splitlines()

    # we don't set a first header for spec definitions so add it here, to avoid
    # having to add it in the docs plugin which renders this.
    header = f"patient {header}"

    return [[token.strip() for token in line.split("|")] for line in [header] + rows]


def convert_output_value(value):
    """Make output value suitable for displaying in table.

    This does the reverse of tests.spec.conftest.parse_value.
    """

    if value is True:
        return "T"
    if value is False:
        return "F"
    if value is None:
        return ""
    return value


class ArgCapturer:
    def __call__(self, table_data, series, expected_output, population=None):
        """Capture the arguments that an instance has been called with.

        The test functions each take a single callable argument which, when the tests
        are run with pytest, is a fixture.  If instead we call the test function with an
        instance of ArgCapturer, we can retrieve the arguments that the callable has
        been called with, and use these to populate the docs.
        """
        self.table_data = table_data
        self.series = series
        self.expected_output = expected_output
        self.set_population = population is not None
