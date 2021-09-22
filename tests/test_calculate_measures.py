from pathlib import Path

import pandas
import pytest

from cohortextractor import Measure, table
from cohortextractor.main import get_measures
from cohortextractor.measure import MeasuresManager


def test_calculate_measures_no_input_file():
    class Cohort:
        code = table("clinical_events").first_by("patient_id").get("code")
        measures = [Measure("test-id", numerator="fish", denominator="litres")]

    measures = get_measures(Cohort)
    measures_manager = MeasuresManager(measures, Path("foo"))
    with pytest.raises(
        AssertionError, match="Expected cohort input file foo not found"
    ):
        list(measures_manager.calculate_measures())


def test_calculate_measures_results():
    class Cohort:
        code = table("clinical_events").first_by("patient_id").get("code")
        measures = [Measure("test-id", numerator="fish", denominator="litres")]

    data = pandas.DataFrame(
        {"fish": [10, 20, 50], "litres": [1, 2, 100]},
        index=["small bowl", "large bowl", "pond"],
    )

    measures = get_measures(Cohort)
    measures_manager = MeasuresManager(measures, Path(""))
    measures_manager._patient_dataframe = data
    actual = list(measures_manager.calculate_measures())
    assert len(actual) == 1
    measure_id, result = actual[0]
    assert measure_id == "test-id"
    assert result.loc["small bowl"]["value"] == 10.0
    assert result.loc["large bowl"]["value"] == 10.0
    assert result.loc["pond"]["value"] == 0.5
