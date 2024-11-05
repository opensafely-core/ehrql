from pathlib import Path

import pytest

from ehrql import quiz
from ehrql.query_engines.sandbox import SandboxQueryEngine
from ehrql.query_language import Dataset
from ehrql.tables.core import patients


@pytest.fixture
def engine():
    path = Path(__file__).parents[2] / "ehrql" / "example-data"
    return SandboxQueryEngine(str(path))


def test_check_answer_wrong_type():
    msg = quiz.check_answer(engine=None, answer=1, expected=Dataset())
    assert msg == "Expected Dataset, got int instead."


def test_check_answer_series_correct(engine):
    msg = quiz.check_answer(
        engine=engine, answer=patients.date_of_birth, expected=patients.date_of_birth
    )
    assert msg == "Correct!"
