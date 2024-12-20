from pathlib import Path

import pytest

from ehrql.query_engines.in_memory_database import PatientColumn
from ehrql.query_engines.debug import EmptyDataset, SandboxQueryEngine
from ehrql.renderers import DISPLAY_RENDERERS
from ehrql.tables import PatientFrame, Series, table


FIXTURES = Path(__file__).parents[2] / "fixtures" / "local_file_engine"


@table
class patients(PatientFrame):
    sex = Series(str)


def test_csv_query_engine_evaluate():
    query_engine = SandboxQueryEngine(FIXTURES)
    result = query_engine.evaluate(patients.sex)
    assert result == PatientColumn({1: "M", 2: "F", 3: None})


@pytest.mark.parametrize(
    "render_format,expected",
    [
        ("ascii", "patient_id\n-----------------"),
        (
            "html",
            "<table><thead><th>patient_id</th></thead><tbody><tr><td></td></tr></tbody></table>",
        ),
    ],
)
def test_empty_dataset_render_(render_format, expected):
    assert EmptyDataset()._render_(DISPLAY_RENDERERS[render_format]).strip() == expected
