from typing import Any

from ehrql.query_engines.sandbox import SandboxQueryEngine
from ehrql.query_language import BaseFrame, BaseSeries, Dataset


def check_answer(
    engine: SandboxQueryEngine, answer: Any, expected: Dataset | BaseFrame | BaseSeries
) -> str:
    if type(answer) is not type(expected):
        return (
            f"Expected {type(expected).__name__}, got {type(answer).__name__} instead."
        )

    ev_answer = engine.evaluate(answer)
    ev_expected = engine.evaluate(expected)

    if ev_answer == ev_expected:
        return "Correct!"
