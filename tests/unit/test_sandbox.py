import re
from io import StringIO
from pathlib import Path

import ehrql
from ehrql.sandbox import run


user_input = """
from ehrql import create_dataset
from ehrql.tables.core import patients
dataset = create_dataset()
dataset.sex = patients.sex
dataset.define_population(patients.date_of_birth > "2000-01-01")
dataset
"""

expected_dataset_output = """
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
    assert expected_dataset_output in captured.out


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
