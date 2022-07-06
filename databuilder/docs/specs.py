import inspect
from importlib import import_module

from tests.spec import toc


def build_specs():
    """Return data describing the specs for use in documentation.

    The structure is derived from tests.spec.toc:
      * the specs are organised into chapters, with one chapter per test package
      * each chapter is split into sections, with one section per test module
      * each section is split into paragraphs, with one paragraph per test function
    """

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

    # Extract the definition of the series.
    series_line = source_lines[ix + 2]
    series = series_line.strip().removesuffix(",")

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
    def __call__(self, table_data, series, expected_output):
        """Capture the arguments that an instance has been called with.

        The test functions each take a single callable argument which, when the tests
        are run with pytest, is a fixture.  If instead we call the test function with an
        instance of ArgCapturer, we can retrieve the arguments that the callable has
        been called with, and use these to populate the docs.
        """
        self.table_data = table_data
        self.series = series
        self.expected_output = expected_output
