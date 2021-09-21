import csv
from pathlib import Path


class Study:
    def __init__(self, study_path, dummy_data_file=None, definition_file=None):
        self._path = Path(__file__).parent.parent.absolute() / "fixtures" / study_path
        self.dummy_data_file = dummy_data_file or "dummy_data.csv"
        self.definition_file = definition_file or "my_cohort.py"

    def definition(self):
        return self._path / self.definition_file

    def code(self):
        return self._path.glob("*.py")

    def expected_results(self):
        return self._path / "results.csv"

    def dummy_data(self):
        return self._path / self.dummy_data_file

    def path(self, filepath):
        return self._path / filepath


class MeasuresStudy(Study):
    def __init__(self, study_path, dummy_data_file=None):
        super(MeasuresStudy, self).__init__(study_path, dummy_data_file)
        self.input_pattern = "cohort.csv"

    def input_files(self):
        return self._path.glob("inputs/*")


def assert_results_equivalent(
    actual_results, expected_results, expected_number_of_results=None
):
    if "*" in actual_results.name:
        results_files = list(actual_results.parent.glob(actual_results.name))
        if expected_number_of_results:
            assert len(results_files) == expected_number_of_results
        for date_file in results_files:
            date_suffix = date_file.name.rsplit("_", 1)[1]
            expected_file = (
                expected_results.parent / f"{expected_results.stem}_{date_suffix}"
            )
            _assert_results(date_file, expected_file)
    else:
        _assert_results(actual_results, expected_results)


def _assert_results(actual_results, expected_results):
    with open(actual_results) as actual_file:
        with open(expected_results) as expected_file:
            actual_data = list(csv.DictReader(actual_file))
            expected_data = list(csv.DictReader(expected_file))
            assert actual_data == expected_data
