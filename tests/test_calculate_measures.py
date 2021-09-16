from pathlib import Path

import pandas

from cohortextractor import Measure, table
from cohortextractor.main import calculate_measures_results


def test_calculate_measures_results():
    class Cohort:
        code = table("clinical_events").first_by("patient_id").get("code")
        measures = [Measure("test-id", numerator="fish", denominator="litres")]

    data = pandas.DataFrame(
        {"fish": [10, 20, 50], "litres": [1, 2, 100]},
        index=["small bowl", "large bowl", "pond"],
    )
    actual = list(calculate_measures_results(Cohort, Path(""), patient_dataframe=data))
    assert len(actual) == 1
    measure_id, result = actual[0]
    assert measure_id == "test-id"
    assert result.loc["small bowl"]["value"] == 10.0
    assert result.loc["large bowl"]["value"] == 10.0
    assert result.loc["pond"]["value"] == 0.5
