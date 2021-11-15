import csv
from pathlib import Path


class Study:
    def __init__(
        self,
        study_path,
        dummy_data_file=None,
        definition_file=None,
        output_file_name=None,
    ):
        self._path = Path(__file__).parent.parent.absolute() / "fixtures" / study_path
        self.dummy_data_file = dummy_data_file or "dummy_data.csv"
        self.definition_file = definition_file or "my_cohort.py"
        self.output_file_name = output_file_name or "cohort.csv"

    def definition(self):
        return self._path / self.definition_file

    def code(self):
        return self._path.glob("*.py")

    def expected_results(self):
        return self._path / "results.csv"

    def dummy_data(self):
        return self._path / self.dummy_data_file


class MeasuresStudy(Study):
    def __init__(
        self,
        study_path,
        dummy_data_file=None,
        definition_file=None,
        output_file_name=None,
        input_pattern=None,
    ):
        super().__init__(study_path, dummy_data_file, definition_file, output_file_name)
        self.output_file_name = "measures_*.csv"
        self.input_pattern = input_pattern or "cohort.csv"

    def input_files(self):
        return self._path.glob("inputs/*")


def assert_results_equivalent(
    actual_results,
    expected_results,
    expected_number_of_results=None,
    match_output_pattern=False,
):
    if match_output_pattern:
        assert (
            expected_number_of_results is not None
        ), "Provide expected number of results when matching an output pattern"
        results_files = list(actual_results.parent.glob(actual_results.name))
        assert len(results_files) == expected_number_of_results
        for results_file in results_files:
            name_parts = [part for part in results_file.stem.split("_", 1) if part][1:]
            name_stem = expected_results.stem.split("_")[0]
            name = "_".join([name_stem, *name_parts])
            expected_results = (
                expected_results.parent / f"{name}{expected_results.suffix}"
            )

            _assert_results(results_file, expected_results)
    else:
        _assert_results(actual_results, expected_results)


def _assert_results(actual_results, expected_results):
    with open(actual_results) as actual_file:
        with open(expected_results) as expected_file:
            actual_data = list(csv.DictReader(actual_file))
            expected_data = list(csv.DictReader(expected_file))
            assert actual_data == expected_data
