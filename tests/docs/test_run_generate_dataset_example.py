import textwrap
import unittest

import pytest

from . import test_complete_examples


def test_run_ehrql_dataset_example(tmp_path):
    example = test_complete_examples.EhrqlExample(
        path="test",
        fence_number=1,
        source=textwrap.dedent(
            """\
            from ehrql import create_dataset
            from ehrql.tables.tpp import patients

            dataset = create_dataset()
            dataset.define_population(patients.exists_for_patient())
            """
        ),
    )
    test_complete_examples.test_ehrql_example(tmp_path, example)


def test_run_ehrql_measures_example(tmp_path):
    example = test_complete_examples.EhrqlExample(
        path="test",
        fence_number=1,
        source=textwrap.dedent(
            """\
            from ehrql import create_measures, months
            from ehrql.tables.tpp import patients

            measures = create_measures()
            measures.define_measure(
                name="test",
                numerator=patients.exists_for_patient(),
                denominator=patients.exists_for_patient(),
                intervals=months(12).starting_on("2020-01-01"),
            )
            """
        ),
    )
    test_complete_examples.test_ehrql_example(tmp_path, example)


def test_run_ehrql_dataset_example_failing(tmp_path):
    example = test_complete_examples.EhrqlExample(
        path="test",
        fence_number=1,
        source=textwrap.dedent(
            """\
            from ehrql import create_dataset

            dataset = create_dataset()
            dataset.define_population(not_a_function())
            """
        ),
    )
    with pytest.raises(test_complete_examples.EhrqlExampleTestError) as exc_info:
        test_complete_examples.test_ehrql_example(tmp_path, example)
    assert type(exc_info.value) is test_complete_examples.EhrqlExampleTestError


def test_run_ehrql_measures_example_failing(tmp_path):
    example = test_complete_examples.EhrqlExample(
        path="test",
        fence_number=1,
        source=textwrap.dedent(
            """\
            from ehrql import create_measures, months
            from ehrql.tables.tpp import patients

            measures = create_measures()
            measures.define_measure(
                name="test",
                numerator=patients.exists_for_patient(),
                denominator=not_a_function(),
                intervals=months(12).starting_on("2020-01-01"),
            )
            """
        ),
    )
    with pytest.raises(test_complete_examples.EhrqlExampleTestError) as exc_info:
        test_complete_examples.test_ehrql_example(tmp_path, example)
    assert type(exc_info.value) is test_complete_examples.EhrqlExampleTestError


def test_run_ehrql_dataset_example_failing_codelist_from_csv_call(tmp_path):
    example = test_complete_examples.EhrqlExample(
        path="test",
        fence_number=1,
        source=textwrap.dedent(
            """\
            from ehrql import codelist_from_csv, create_dataset
            from ehrql.tables.tpp import patients

            codes = codelist_from_csv()

            dataset = create_dataset()
            dataset.define_population(patients.exists_for_patient())
            """
        ),
    )

    with pytest.raises(
        test_complete_examples.EhrqlExampleTestError,
        match=r"generate_dataset failed for example",
    ) as exc_info:
        test_complete_examples.test_ehrql_example(tmp_path, example)
    assert type(exc_info.value) is test_complete_examples.EhrqlExampleTestError


def test_run_ehrql_measures_example_failing_codelist_from_csv_call(tmp_path):
    example = test_complete_examples.EhrqlExample(
        path="test",
        fence_number=1,
        source=textwrap.dedent(
            """\
            from ehrql import create_measures, months
            from ehrql.tables.tpp import patients

            codes = codelist_from_csv()

            measures = create_measures()
            measures.define_measure(
                name="test",
                numerator=patients.exists_for_patient(),
                denominator=patients.exists_for_patient(),
                intervals=months(12).starting_on("2020-01-01"),
            )
            """
        ),
    )

    with pytest.raises(
        test_complete_examples.EhrqlExampleTestError,
        match=r"generate_measures failed for example",
    ) as exc_info:
        test_complete_examples.test_ehrql_example(tmp_path, example)
    assert type(exc_info.value) is test_complete_examples.EhrqlExampleTestError


def test_run_ehrql_dataset_example_gives_unreadable_csv(tmp_path):
    example = test_complete_examples.EhrqlExample(
        path="test",
        fence_number=1,
        source=textwrap.dedent(
            """\
            from ehrql import create_dataset
            from ehrql.tables.tpp import patients

            dataset = create_dataset()
            dataset.define_population(patients.exists_for_patient())
            """
        ),
    )
    with unittest.mock.patch("ehrql.main.generate_dataset", return_value=None):
        with pytest.raises(
            test_complete_examples.EhrqlExampleTestError,
            match=r"Check of CSV output failed for example",
        ) as exc_info:
            test_complete_examples.test_ehrql_example(tmp_path, example)
    assert type(exc_info.value) is test_complete_examples.EhrqlExampleTestError


def test_run_ehrql_measures_example_gives_unreadable_csv(tmp_path):
    example = test_complete_examples.EhrqlExample(
        path="test",
        fence_number=1,
        source=textwrap.dedent(
            """\
            from ehrql import create_measures, months
            from ehrql.tables.tpp import patients

            measures = create_measures()
            measures.define_measure(
                name="test",
                numerator=patients.exists_for_patient(),
                denominator=patients.exists_for_patient(),
                intervals=months(12).starting_on("2020-01-01"),
            )
            """
        ),
    )
    with unittest.mock.patch("ehrql.main.generate_measures", return_value=None):
        with pytest.raises(
            test_complete_examples.EhrqlExampleTestError,
            match=r"Check of CSV output failed for example",
        ) as exc_info:
            test_complete_examples.test_ehrql_example(tmp_path, example)
    assert type(exc_info.value) is test_complete_examples.EhrqlExampleTestError


def test_run_ehrql_non_matching_example(tmp_path):
    example = test_complete_examples.EhrqlExample(
        path="test",
        fence_number=1,
        source=textwrap.dedent(
            """\
            from ehrql import create_measures
            """
        ),
    )
    with pytest.raises(
        test_complete_examples.EhrqlExampleTestError,
    ) as exc_info:
        test_complete_examples.test_ehrql_example(tmp_path, example)
    assert type(exc_info.value) is test_complete_examples.EhrqlExampleTestError


def test_run_ehrql_cannot_include_measures_and_dataset(tmp_path):
    example = test_complete_examples.EhrqlExample(
        path="test",
        fence_number=1,
        source=textwrap.dedent(
            """\
            from ehrql import create_measures, create_dataset
            dataset = create_dataset()
            measures = create_measures()
            """
        ),
    )
    with pytest.raises(
        test_complete_examples.EhrqlExampleTestError,
    ) as exc_info:
        test_complete_examples.test_ehrql_example(tmp_path, example)
    assert type(exc_info.value) is test_complete_examples.EhrqlExampleTestError


def test_run_ehrql_partial_dataset_example(tmp_path):
    example = test_complete_examples.EhrqlExample(
        path="test",
        fence_number=1,
        source=textwrap.dedent(
            """\
            dataset.define_population(patients.exists_for_patient())
            """
        ),
    )
    test_complete_examples.test_ehrql_example(tmp_path, example)


def test_run_ehrql_partial_dataset_example_no_population_defined(tmp_path):
    example = test_complete_examples.EhrqlExample(
        path="test",
        fence_number=1,
        source=textwrap.dedent(
            """\
            dataset.year = patients.date_of_birth.year
            """
        ),
    )
    test_complete_examples.test_ehrql_example(tmp_path, example)
