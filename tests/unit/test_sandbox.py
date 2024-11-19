import re
from io import StringIO
from pathlib import Path

import ehrql
from ehrql.sandbox import run


user_input = """
from ehrql import create_dataset, days
from ehrql.tables.core import patients
patients.date_of_birth
patients.date_of_birth + days(1) - patients.date_of_birth
patients
dataset = create_dataset()
dataset.sex = patients.sex
dataset
dataset.define_population(patients.date_of_birth > "2000-01-01")
dataset
"""

expected_series_output_1 = """
patient_id        | value
------------------+------------------
1                 | 1980-01-01
2                 | 1990-02-01
3                 | 2000-03-01
4                 | 2010-04-01
""".strip()

expected_series_output_2 = """
patient_id        | value
------------------+------------------
1                 | 1
2                 | 1
3                 | 1
4                 | 1
""".strip()

expected_frame_output = """
patient_id        | date_of_birth     | sex               | date_of_death
------------------+-------------------+-------------------+------------------
1                 | 1980-01-01        | female            | None
2                 | 1990-02-01        | male              | None
3                 | 2000-03-01        | female            | None
4                 | 2010-04-01        | male              | None
""".strip()

expected_dataset_output_1 = """
patient_id        | sex
------------------+------------------
1                 | female
2                 | male
3                 | female
4                 | male
""".strip()

expected_dataset_output_2 = """
patient_id        | sex
------------------+------------------
3                 | female
4                 | male
""".strip()


def test_run(capsys, monkeypatch):
    monkeypatch.setattr("sys.stdin", StringIO(user_input))
    dummy_tables_path = Path(__file__).parents[1] / "fixtures" / "sandbox"
    run(dummy_tables_path)
    captured = capsys.readouterr()
    assert expected_series_output_1 in captured.out, captured.out
    assert expected_series_output_2 in captured.out, captured.out
    assert expected_frame_output in captured.out
    assert expected_dataset_output_1 in captured.out
    assert expected_dataset_output_2 in captured.out


def test_run_with_empty_dataset(capsys, monkeypatch):
    monkeypatch.setattr("sys.stdin", StringIO("from ehrql import Dataset; Dataset()"))
    dummy_tables_path = Path(__file__).parents[1] / "fixtures" / "sandbox"
    run(dummy_tables_path)
    captured = capsys.readouterr()
    assert captured.out == ">>> Dataset()\n>>> "


def test_traceback_trimmed(capsys, monkeypatch):
    monkeypatch.setattr(
        "sys.stdin",
        StringIO(
            "from ehrql.tables.core import patients\n"
            "patients.date_of_birth == patients.sex"
        ),
    )
    dummy_tables_path = Path(__file__).parents[1] / "fixtures" / "sandbox"
    run(dummy_tables_path)
    captured = capsys.readouterr()
    # We shouldn't have any references to ehrql code in the traceback
    ehrql_root = str(Path(ehrql.__file__).parent)
    assert not re.search(re.escape(ehrql_root), captured.err)
