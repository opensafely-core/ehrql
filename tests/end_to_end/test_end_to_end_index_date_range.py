import pytest

from .utils import assert_results_equivalent


@pytest.mark.parametrize(
    "definition_file,output_file,error",
    [
        (
            "cohort_no_valid_class_or_function.py",
            "cohort_*.csv",
            "A study definition must contain one and only one 'cohort' function or 'Cohort' class",
        ),
        (
            "cohort_invalid_function_args.py",
            "cohort_*.csv",
            "A study definition with index_date_range must pass a single index_date argument to the 'cohort' function",
        ),
        (
            "my_cohort.py",
            "cohort.csv",
            "No output pattern found in output file",
        ),
    ],
)
def test_index_date_range_cohort_definition_errors(
    load_study,
    cohort_extractor_in_process_no_database,
    definition_file,
    output_file,
    error,
):
    study = load_study(
        "end_to_end_index_date_range",
        definition_file=definition_file,
        output_file_name=output_file,
    )
    with pytest.raises(ValueError, match=error):
        cohort_extractor_in_process_no_database(
            study,
            backend="tpp",
            use_dummy_data=False,
        )


def test_dummy_data_with_index_date_range(
    load_study, cohort_extractor_in_process_no_database
):
    study = load_study(
        "end_to_end_index_date_range",
        dummy_data_file="dummy_data_*.csv",
        output_file_name="cohort_*.csv",
    )
    actual_results = cohort_extractor_in_process_no_database(study, use_dummy_data=True)
    assert_results_equivalent(
        actual_results,
        study.expected_results(),
        expected_number_of_results=3,
        match_output_pattern=True,
    )
