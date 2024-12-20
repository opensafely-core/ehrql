import sys
from pathlib import Path
from typing import Any

import ehrql.debugger
from ehrql.query_engines.debug import DebugQueryEngine, EmptyDataset
from ehrql.query_engines.in_memory_database import (
    EventColumn,
    EventTable,
    PatientColumn,
    PatientTable,
)
from ehrql.query_language import BaseFrame, BaseSeries, Dataset


def check_answer(
    engine: DebugQueryEngine, answer: Any, expected: Dataset | BaseFrame | BaseSeries
) -> str:
    message = check_type(answer, expected)
    if message:
        return message

    ev_answer = engine.evaluate(answer)
    ev_expected = engine.evaluate(expected)

    message = check_type(ev_answer, ev_expected)
    if message:
        return message

    if ev_answer == ev_expected:
        return "Correct!"

    checks = [
        check_dataset_not_empty,
        check_dataset_columns,
        check_patient_ids,
        check_patient_table_values,
        check_patient_column_values,
        check_event_row_ids,
        check_event_table_values,
        check_event_column_values,
    ]

    for check in checks:
        message = check(ev_answer, ev_expected)
        if message is None:
            continue  # to the next check
        return message
    return "\n".join(
        [
            "Incorrect answer.",
            "Expected:",
            str(ev_expected),
            "Got:",
            str(ev_answer),
        ]
    )


def get_type_name(obj: Any) -> str:
    # Simplify the type name for better error messages
    if isinstance(obj, BaseFrame):
        return "Table"
    elif isinstance(obj, BaseSeries):
        return "Series"
    return type(obj).__name__


def check_type(answer: Any, expected: Any) -> str:
    if not isinstance(answer, type(expected)):
        answer_type_name = get_type_name(answer)
        expected_type_name = get_type_name(expected)

        if answer_type_name == "EmptyDataset":
            return None  # Return a different message for empty datasets
        if answer_type_name != expected_type_name:
            # Only return an error message if it is helpful
            return f"Expected {expected_type_name}, got {answer_type_name} instead."
    return None


def check_dataset_not_empty(ev_answer: Any, ev_expected: Any) -> str | None:
    if isinstance(ev_answer, EmptyDataset):
        if isinstance(ev_expected, EmptyDataset):
            return "Correct!"  # Special case: Not an error
        return "The dataset is empty."
    return None


def check_dataset_columns(ev_answer: Any, ev_expected: Any) -> str | None:
    # Named so because we do not expect PatientTables from Frames to have varying columns
    if isinstance(ev_expected, PatientTable):
        return _check_missing_extra(
            ev_answer, ev_expected, "column", getter=lambda t: t.name_to_col.keys()
        )
    return None


def check_patient_ids(ev_answer: Any, ev_expected: Any) -> str | None:
    def check(_ev_answer, _ev_expected) -> str | None:
        return _check_missing_extra(
            _ev_answer,
            _ev_expected,
            "patient",
            getter=lambda c: c.patients(),
        )

    if isinstance(ev_expected, PatientColumn):
        return check(ev_answer, ev_expected)
    if isinstance(ev_expected, PatientTable):
        return _check_table_then_columns_one_by_one(
            ev_answer,
            ev_expected,
            check,
            column_names=list(ev_expected.name_to_col.keys() - {"patient_id"}),
        )
    return None


def check_patient_table_values(ev_answer: Any, ev_expected: Any) -> str | None:
    if isinstance(ev_expected, PatientTable):
        return _check_columns_one_by_one(
            ev_answer,
            ev_expected,
            check_patient_column_values,
            column_names=list(ev_expected.name_to_col.keys() - {"patient_id"}),
            # Patient ID handled separately
        )
    return None


def check_patient_column_values(
    ev_answer, ev_expected, column_name: str | None = None
) -> str | None:
    if isinstance(ev_expected, PatientColumn):
        column_name = f" `{column_name}` " if column_name else " "
        incorrect = sorted(
            ev_answer.patient_to_value.items() - ev_expected.patient_to_value.items()
        )
        # Last check for Patient Frames/Series; Expect incorrect to be non-empty
        # Only show the first incorrect value
        for k, v in incorrect:  # pragma: no branch
            return f"Incorrect{column_name}value for patient {k}: expected {str(ev_expected[k])}, got {str(v)} instead."
    return None


def check_event_row_ids(ev_answer: Any, ev_expected: Any) -> str | None:
    def check(_ev_answer, _ev_expected) -> str | None:
        return _check_missing_extra(
            _ev_answer,
            _ev_expected,
            "row",
            getter=lambda c: set(row["row_id"] for row in c.to_records()),
        )

    if isinstance(ev_expected, EventColumn):
        return check(ev_answer, ev_expected)
    if isinstance(ev_expected, EventTable):
        return _check_table_then_columns_one_by_one(
            ev_answer,
            ev_expected,
            check,
            column_names=list(
                ev_expected.name_to_col.keys() - {"patient_id", "row_id"}
            ),
        )
    return None


# Cannot find a wrong answer that triggers this, but a wild user answer might
# So still include this check in the list but pragma: no cover it
def check_event_table_values(
    ev_answer: Any, ev_expected: Any
) -> str | None:  # pragma: no cover
    if isinstance(ev_expected, EventTable):
        return _check_columns_one_by_one(
            ev_answer,
            ev_expected,
            check_event_column_values,
            column_names=list(
                ev_expected.name_to_col.keys() - {"patient_id", "row_id"}
            ),
            # Patient ID and Row ID handled separately
        )
    return None


def check_event_column_values(
    ev_answer, ev_expected, column_name: str | None = None
) -> str | None:
    if isinstance(ev_expected, EventColumn):
        column_name = f" `{column_name}` " if column_name else " "
        records_ans = set(tuple(rec.values()) for rec in ev_answer.to_records())
        records_exp = set(tuple(rec.values()) for rec in ev_expected.to_records())
        incorrect = sorted(records_ans - records_exp)
        # Last check for Event Frames/Series; Expect incorrect to be non-empty
        # Only show the first incorrect value
        for p, r, v in incorrect:  # pragma: no branch
            return f"Incorrect{column_name}value for patient {p}, row {r}: expected {str(ev_expected[p][r])}, got {str(v)} instead."
    return None


# Utils functions
def get_items_missing_extra(
    set_answer: set,
    set_expected: set,
    item_name: str,
) -> tuple[str | None, str | None]:
    missing = list(map(str, sorted(set_expected - set_answer)))
    missing = f"Missing {item_name}(s): {', '.join(missing)}." if missing else None
    extra = list(map(str, sorted(set_answer - set_expected)))
    extra = f"Found extra {item_name}(s): {', '.join(extra)}." if extra else None
    return missing, extra


def _check_missing_extra(
    ev_answer: Any,
    ev_expected: Any,
    item_name: str,
    getter: callable,
) -> str | None:
    missing_columns, extra_columns = get_items_missing_extra(
        getter(ev_answer), getter(ev_expected), item_name
    )
    if missing_columns or extra_columns:
        return "\n".join(filter(None, [missing_columns, extra_columns]))
    return None


def _check_columns_one_by_one(
    ev_answer: Any,
    ev_expected: Any,
    check_column: callable,
    column_names: list[str],
) -> str | None:
    for name in column_names:
        msg = check_column(ev_answer[name], ev_expected[name], name)
        if msg is None:
            continue
        return msg


def _check_table_then_columns_one_by_one(
    ev_answer: Any,
    ev_expected: Any,
    check: callable,
    column_names: list[str],
):
    def check_column(col_ans, col_exp, column_name: str | None = None) -> str | None:
        msg = check(col_ans, col_exp)
        if msg:  # pragma: no cover
            return f"Column `{column_name}`:\n" + msg
        return msg

    msg_table = check(ev_answer, ev_expected)
    if msg_table:
        return msg_table
    return _check_columns_one_by_one(
        ev_answer,
        ev_expected,
        check_column,
        column_names=column_names,
    )


class Questions:
    def __init__(self):
        self.questions = {}
        self.engine = DebugQueryEngine(None)

    def set_dummy_tables_path(self, path):
        path = Path(path)
        self.engine.dsn = path
        # This isn't particularly nice but we want to ensure that any `show()` calls
        # made when completing the quiz always use the same dummy tables as the quiz
        # itself, regardless of how the quiz script was invoked. This kind of global
        # nastiness seems tolerable in the context of the quiz, and worth it for
        # avoiding potential confusion.
        if ehrql.debugger.DEBUG_QUERY_ENGINE is not None:
            ehrql.debugger.DEBUG_QUERY_ENGINE.dsn = path

    def __setitem__(self, index, question):
        question.index = index
        question.engine = self.engine
        self.questions[index] = question

    def __getitem__(self, index):
        return self.questions[index]

    def get_all(self):
        return self.questions.values()

    def summarise(self):
        summarise(self.questions)


class Question:
    def __init__(
        self,
        prompt: str,
        index: int | None = None,
        engine: DebugQueryEngine | None = None,
    ):
        self.prompt = prompt
        self.index = index
        self.expected = None
        self.engine = engine
        self.attempted = False
        self.correct = False
        self._hint = ""

    def check(self, answer: Any = ...) -> str:
        if answer is not ...:
            self.attempted = True
            engine = self.engine or self.get_engine()
            message = check_answer(engine, answer, self.expected)
            self.correct = message == "Correct!"
        else:
            message = "Skipped."
        message = f"Question {self.index}\n{message}\n"
        print(message, file=sys.stderr)

    def hint(self):
        message_lines = [f"Hint for question {self.index}:"]

        if len(self._hint) > 0:
            message_lines.append(self._hint)

        message_lines.append(
            "Remember that you can use show() to take a look at your "
            "output. So instead of calling\n\n"
            f"questions[{self.index}].check(..your answer..)\n\n"
            "you can call\n\n"
            "show(..your answer..)\n\n"
            "to see if you're on the right track.\n"
        )
        print("\n\n".join(message_lines), file=sys.stderr)

    @staticmethod
    def get_engine() -> DebugQueryEngine:
        path = Path(__file__).parent / "example-data"
        return DebugQueryEngine(str(path))


def summarise(questions: dict[int, Question]) -> None:
    correct = sum(q.attempted and q.correct for q in questions.values())
    incorrect = sum(q.attempted and not q.correct for q in questions.values())
    unanswered = sum(not q.attempted for q in questions.values())

    message = "\n".join(
        [
            "\n\nSummary of your results",
            f"Correct: {correct}",
            f"Incorrect: {incorrect}",
            f"Unanswered: {unanswered}",
        ]
    )
    print(message, file=sys.stderr)
