import re
from io import StringIO
from pathlib import Path

import ehrql
from ehrql.sandbox import run


user_input = """
from ehrql import Dataset
from ehrql.tables.tpp import patients
patients.date_of_birth
patients
dataset = Dataset()
dataset.sex = patients.sex
dataset
dataset.define_population(patients.date_of_birth > "2000-01-01")
dataset
"""

expected_series_output = """
 1 | 1980-01-01
 2 | 1990-02-01
 3 | 2000-03-01
 4 | 2010-04-01
""".strip()

expected_frame_output = """
patient_id        | date_of_birth     | sex               | date_of_death
------------------+-------------------+-------------------+------------------
1                 | 1980-01-01        | F                 | None
2                 | 1990-02-01        | M                 | None
3                 | 2000-03-01        | F                 | None
4                 | 2010-04-01        | M                 | None
""".strip()

expected_dataset_output_1 = """
patient_id        | sex
------------------+------------------
1                 | F
2                 | M
3                 | F
4                 | M
""".strip()

expected_dataset_output_2 = """
patient_id        | sex
------------------+------------------
3                 | F
4                 | M
""".strip()


def test_run(capsys, monkeypatch):
    monkeypatch.setattr("sys.stdin", StringIO(user_input))
    dummy_tables_path = Path(__file__).parents[1] / "fixtures" / "sandbox"
    run(dummy_tables_path)
    captured = capsys.readouterr()
    assert expected_series_output in captured.out
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
            "from ehrql.tables.tpp import patients\n"
            "patients.date_of_birth == patients.sex"
        ),
    )
    dummy_tables_path = Path(__file__).parents[1] / "fixtures" / "sandbox"
    run(dummy_tables_path)
    captured = capsys.readouterr()
    # We shouldn't have any references to ehrql code in the traceback
    ehrql_root = str(Path(ehrql.__file__).parent)
    assert not re.search(re.escape(ehrql_root), captured.err)
