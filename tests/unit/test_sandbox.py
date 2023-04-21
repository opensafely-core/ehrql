from io import StringIO
from pathlib import Path

from ehrql.sandbox import run


user_input = """
from databuilder.tables.beta.tpp import patients
patients.date_of_birth
patients
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


def test_run(capsys, monkeypatch):
    monkeypatch.setattr("sys.stdin", StringIO(user_input))
    dummy_tables_path = Path(__file__).parents[1] / "fixtures" / "sandbox"
    run(dummy_tables_path)
    captured = capsys.readouterr()
    assert expected_series_output in captured.out
    assert expected_frame_output in captured.out
