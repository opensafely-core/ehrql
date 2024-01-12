import copy
import csv
import inspect
import re
import unittest.mock
import uuid
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path

import markdown
import mkdocs.config
import pytest

import ehrql.main


def get_markdown_extension_configuration():
    """Returns a dictionary representing the mkdocs.yml Markdown extension
    configuration.

    It should only be required to run this function once,
    at the start of these tests."""
    config_path = Path(__file__).parents[2] / "mkdocs.yml"
    config = mkdocs.config.load_config(config_file_path=str(config_path))
    assert "pymdownx.superfences" in config["markdown_extensions"]
    return config["mdx_configs"]


MARKDOWN_EXTENSION_CONFIGURATION = get_markdown_extension_configuration()


@dataclass
class MarkdownFence:
    """Represents a Markdown fence."""

    source: str
    language: str


class MarkdownFenceExtractor:
    """Extracts fences from a markdown.Markdown object using the SuperFences extension.

    See https://facelessuser.github.io/pymdown-extensions/extensions/superfences/
    """

    def __init__(self, content):
        self.fences = []
        self.extension_configs = self._configure_superfences()
        self._extract_fences(content)

    def _fence_null_format(
        self,
        src,
        language,
        css_class,
        options,
        md,
        **kwargs,
    ) -> str:
        """Extract the fences in the same way
        as the SuperFences extension does, and make them accessible to the test code.

        Returns an empty string.

        This null formatter exists only for this purpose.
        See https://facelessuser.github.io/pymdown-extensions/extensions/superfences/#formatters

        "All formatters should return a string as HTML."

        We don't require the formatted text,
        only that this method is run and we can access the source
        and language."""
        self.fences.append(MarkdownFence(source=src, language=language))
        return ""

    def _configure_superfences(self):
        """Retrieves the existing extensions settings from the mkdocs.yml
        configuration, replacing any custom SuperFences fences with a special
        test custom fence to extract all fences."""
        config = copy.deepcopy(MARKDOWN_EXTENSION_CONFIGURATION)
        config["pymdownx.superfences"]["custom_fences"] = [
            {
                # "name" specifies fences to extract.
                # "*" indicates fences unhandled by other custom fences;
                # as we have no other custom fences, "*" processes all fences.
                "name": "*",
                "class": "test",
                "format": self._fence_null_format,
            },
        ]
        return config

    def _extract_fences(self, content):
        markdown.Markdown(
            extensions=["pymdownx.superfences"],
            extension_configs=self.extension_configs,
        ).convert(content)


class EhrqlExampleDefinitionType(Enum):
    """Identifies the different kinds of ehrQL definitions."""

    DATASET = auto()
    MEASURE = auto()


@dataclass
class EhrqlExample:
    """Stores details of an ehrQL definition example.

    The origin of such an example may be a Markdown fence,
    or a standalone Python module.

    Such examples to be tested should be complete examples,
    not partial snippets of examples.

    An EhrqlExample itself is not validated as a correct ehrQL definition example at creation,
    but used as part of the tests to validate the ehrQL."""

    path: Path
    # This fence number count includes all fences,
    # not just the ehrQL fences.
    # Standalone Python modules are not given a fence number.
    fence_number: int | None
    source: str
    definition_type: EhrqlExampleDefinitionType | None = field(init=False)

    def __post_init__(self):
        self.definition_type = self._get_definition_type()

    def relative_path(self):
        """Return the relative path of the dataset definition source file
        to the source code root."""
        source_code_path = Path(__file__).parents[2]
        return self.path.relative_to(source_code_path)

    def _get_definition_type(self):
        """Return the type of ehrQL definition or None if no match."""
        definition_types = {
            "create_dataset()": EhrqlExampleDefinitionType.DATASET,
            "create_measures()": EhrqlExampleDefinitionType.MEASURE,
        }

        definition_function_call_matches = set(
            re.findall(
                r"(?:create_dataset\(\))|(?:create_measures\(\))",
                self.source,
            )
        )
        if len(definition_function_call_matches) != 1:
            # Either no match,
            # or we have both create_dataset() and create_measures().
            # Both of these cases are invalid.
            return None

        (definition_function_call_string,) = definition_function_call_matches
        assert definition_function_call_string in definition_types
        return definition_types[definition_function_call_string]


def discover_paths(glob_string):
    """Generate a list of matching files for a glob in the documentation source path."""
    docs_path = Path(__file__).parents[2] / "docs"
    return docs_path.glob(glob_string)


def find_complete_ehrql_examples_in_markdown(file):
    """Yields extracted code blocks labelled as ```ehrql from a Markdown file.

    Incomplete ehrQL dataset definitions should be labelled as ```python,
    and not with ```ehrql."""
    f = MarkdownFenceExtractor(file.read())

    for fence_number, fence in enumerate(f.fences, start=1):
        if fence.language == "ehrql":
            example = EhrqlExample(
                path=Path(file.name),
                fence_number=fence_number,
                source=fence.source,
            )
            yield example


def generate_complete_ehrql_examples():
    """Yields all complete EhrqlExamples from the Markdown documentation."""
    markdown_paths = list(discover_paths("**/*.md"))
    assert len(markdown_paths) > 0, "No Markdown files found"

    for p in markdown_paths:
        with open(p) as f:
            yield from find_complete_ehrql_examples_in_markdown(f)

    python_source_paths = list(discover_paths("**/*.py"))
    assert len(python_source_paths) > 0, "No .py files found"

    for p in python_source_paths:
        with open(p) as f:
            content = f.read()
        assert len(content) > 0
        yield EhrqlExample(
            path=Path(f.name),
            fence_number=None,
            source=content,
        )


def create_example_test_case_id(example):
    """Returns a test case ID for pytest from a specific EhrqlExample."""
    test_id = f"{example.relative_path()}"
    if example.fence_number is not None:
        test_id += f"; fence {example.fence_number}"
    return test_id


def validate_dataset_output(dataset_path):
    """Validates that an output dataset file is a CSV."""
    with open(dataset_path) as f:
        csv_content = f.readlines()

    # If the dataset definition works, we should have a valid CSV.
    assert len(csv_content) > 0, "CSV is empty for dataset"

    # Check we can read the CSV content.
    csv_reader = csv.DictReader(csv_content)
    for row in csv_reader:
        pass


class EhrqlExampleTestError(Exception):
    pass


@pytest.mark.parametrize(
    "example",
    generate_complete_ehrql_examples(),
    ids=create_example_test_case_id,
)
def test_ehrql_example(tmp_path, example):
    tmp_filename_base = str(uuid.uuid4())

    tmp_example_path = tmp_path / (tmp_filename_base + ".py")
    tmp_example_path.write_text(example.source)

    tmp_output_path = tmp_path / (tmp_filename_base + ".csv")

    code_column_name = "code"
    category_column_name = "category"
    tmp_codelist_path = tmp_path / (tmp_filename_base + "_codelist.csv")
    tmp_codelist_path.write_text(
        f"{code_column_name},{category_column_name}\n"
        "not_a_real_code!,not_a_real_category!"
    )

    codelist_fn = ehrql.codelist_from_csv

    def wrapped_codelist_from_csv(*args, **kwargs):
        """Returns the result from ehrql.codelist_from_csv.

        This is used to monkeypatch the real ehrql.codelist_from_csv
        so that we can use a mock CSV, but it:

        * validates the function arguments
        * calls the real function with the mock CSV data

        Different documentation examples may refer to different CSV columns.
        Because of this, we change the arguments passed to codelist_from_csv().
        """
        codelist_fn_signature = inspect.signature(codelist_fn)
        try:
            codelist_fn_signature.bind(*args, **kwargs)
        except TypeError as e:
            e.add_note("codelist_from_csv() given incorrect arguments")
            raise e

        return codelist_fn(
            filename=tmp_codelist_path,
            column=code_column_name,
            category_column=category_column_name,
        )

    def wrapped_load_dataset_definition(definition_file, user_args, _):
        """Wraps ehrql.load_dataset_definition to use the unsafe version
        that runs the dataset definition in the same process,
        without sandboxing.

        This is to remove the additional environ argument that is not used in
        load_dataset_definition_unsafe."""
        return ehrql.loaders.load_dataset_definition_unsafe(definition_file, user_args)

    def wrapped_load_measure_definitions(definition_file, user_args, _):
        """Wraps ehrql.load_measure_definitions to use the unsafe version
        that runs the dataset definition in the same process,
        without sandboxing.

        This is to remove the additional environ argument that is not used in
        load_measure_definitions_unsafe."""
        return ehrql.loaders.load_measure_definitions_unsafe(definition_file, user_args)

    formatted_example = f"\nEXAMPLE FILENAME {example.path}\nEXAMPLE START\n{example.source}\nEXAMPLE END"

    match example.definition_type:
        case EhrqlExampleDefinitionType.DATASET:
            generate_fn = ehrql.main.generate_dataset
            wrapped_fn = wrapped_load_dataset_definition
            ehrql_fn_name_to_patch = "ehrql.main.load_dataset_definition"
        case EhrqlExampleDefinitionType.MEASURE:
            generate_fn = ehrql.main.generate_measures
            wrapped_fn = wrapped_load_measure_definitions
            ehrql_fn_name_to_patch = "ehrql.main.load_measure_definitions"
        case _:
            raise EhrqlExampleTestError(
                f"example did not contain create_dataset() or create_measures(): {formatted_example}"
            )

    with (
        # Patch out the sandbox for now to use the unsafe loader.
        # This allows the subsequent monkeypatching of codelist_from_csv.
        # By patching load_dataset_definition,
        # we can still use the existing ehrql.main.generate_dataset function.
        unittest.mock.patch(
            ehrql_fn_name_to_patch,
            wraps=wrapped_fn,
        ),
        unittest.mock.patch(
            "ehrql.codelist_from_csv",
            wraps=wrapped_codelist_from_csv,
        ),
        # There is no codelist code that satisfies constraints of all code systems,
        # so patch out the validity check and just pass in a fake codelist.
        unittest.mock.patch(
            "ehrql.codes.BaseCode.__post_init__",
            return_value=None,
        ),
    ):
        args = [tmp_example_path, tmp_output_path]
        kwargs = {
            name: None
            for name, param in inspect.signature(generate_fn).parameters.items()
            if param.kind == param.KEYWORD_ONLY
        }
        kwargs.update({"environ": {}, "user_args": ()})
        try:
            generate_fn(*args, **kwargs)
        except Exception as e:
            generate_fn_name = generate_fn.__name__.rpartition(".")[-1]
            raise EhrqlExampleTestError(
                f"{generate_fn_name} failed for example: {formatted_example}"
            ) from e

    try:
        validate_dataset_output(tmp_output_path)
    except Exception as e:
        raise EhrqlExampleTestError(
            f"Check of CSV output failed for example: \n{formatted_example}"
        ) from e
