import csv
from pathlib import Path


class Study:
    def __init__(self, study_path, dummy_data_file=None):
        self._path = Path(__file__).parent.parent.absolute() / "fixtures" / study_path
        self.dummy_data_file = dummy_data_file or "dummy_data.csv"

    def definition(self):
        return self._path / "my_cohort.py"

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


def assert_results_equivalent(actual_results, expected_results):
    with open(actual_results) as actual_file:
        with open(expected_results) as expected_file:
            actual_data = list(csv.DictReader(actual_file))
            expected_data = list(csv.DictReader(expected_file))
        assert actual_data == expected_data
