from typing import Any

import marimo as mo

from ehrql import create_dataset
from ehrql.query_engines.in_memory_database import (
    EventColumn,
    EventTable,
    PatientColumn,
    PatientTable,
)
from ehrql.query_engines.sandbox import EmptyDataset, SandboxQueryEngine
from ehrql.query_language import BaseFrame, BaseSeries, Dataset
from ehrql.tables.core import clinical_events, patients


def check_answer(
    engine: SandboxQueryEngine, answer: Any, expected: Dataset | BaseFrame | BaseSeries
) -> str:
    message = check_type(answer, expected)
    if message:
        return message

    ev_answer = evaluate(engine, answer)
    ev_expected = evaluate(engine, expected)

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


def evaluate(
    engine: SandboxQueryEngine, answer: Dataset | BaseFrame | BaseSeries
) -> Any:
    if isinstance(answer, Dataset):
        return engine.evaluate_dataset(answer)
    return engine.evaluate(answer)


def check_dataset_not_empty(ev_ans: Any, ev_exp: Any) -> str | None:
    if isinstance(ev_ans, EmptyDataset):
        if isinstance(ev_exp, EmptyDataset):
            return "Correct!"  # Special case: Not an error
        return "The dataset is empty."
    return None


def check_dataset_columns(ev_ans: Any, ev_exp: Any) -> str | None:
    # Named so because we do not expect PatientTables from Frames to have varying columns
    if isinstance(ev_exp, PatientTable):
        return _check_missing_extra(
            ev_ans, ev_exp, "column", getter=lambda t: t.name_to_col.keys()
        )
    return None


def check_patient_ids(ev_ans: Any, ev_exp: Any) -> str | None:
    if isinstance(ev_exp, PatientTable) or isinstance(ev_exp, PatientColumn):
        return _check_missing_extra(
            ev_ans, ev_exp, "patient", getter=lambda t: t.patients()
        )
    return None


def check_patient_table_values(ev_ans: Any, ev_exp: Any) -> str | None:
    if isinstance(ev_exp, PatientTable):
        return _check_columns_one_by_one(
            ev_ans,
            ev_exp,
            check_patient_column_values,
            column_names=list(ev_exp.name_to_col.keys() - {"patient_id"}),
            # Patient ID handled separately
        )
    return None


def check_patient_column_values(
    ev_ans, ev_exp, column_name: str | None = None
) -> str | None:
    if isinstance(ev_exp, PatientColumn):
        column_name = f" `{column_name}` " if column_name else " "
        incorrect = sorted(
            ev_ans.patient_to_value.items() - ev_exp.patient_to_value.items()
        )
        for k, v in incorrect:  # Only show the first incorrect value
            return f"Incorrect{column_name}value for patient {k}: expected {str(ev_exp[k])}, got {str(v)} instead."
    return None


def check_event_row_ids(ev_ans: Any, ev_exp: Any) -> str | None:
    if isinstance(ev_exp, EventTable) or isinstance(ev_exp, EventColumn):
        return _check_missing_extra(
            ev_ans,
            ev_exp,
            "row",
            getter=lambda t: set(row["row_id"] for row in t.to_records()),
        )

    return None


def check_event_table_values(ev_ans: Any, ev_exp: Any) -> str | None:
    if isinstance(ev_exp, EventTable):
        return _check_columns_one_by_one(
            ev_ans,
            ev_exp,
            check_event_column_values,
            column_names=list(ev_exp.name_to_col.keys() - {"patient_id", "row_id"}),
            # Patient ID and Row ID handled separately
        )
    return None


def check_event_column_values(
    ev_ans, ev_exp, column_name: str | None = None
) -> str | None:
    if isinstance(ev_exp, EventColumn):
        column_name = f" `{column_name}` " if column_name else " "
        records_ans = set(tuple(rec.values()) for rec in ev_ans.to_records())
        records_exp = set(tuple(rec.values()) for rec in ev_exp.to_records())
        incorrect = sorted(records_ans - records_exp)
        for p, r, v in incorrect:  # Only show the first incorrect value
            return f"Incorrect{column_name}value for patient {p}, row {r}: expected {str(ev_exp[p][r])}, got {str(v)} instead."
    return None


# Utils functions
def get_items_missing_extra(
    set_ans: set,
    set_exp: set,
    item_name: str,
) -> tuple[str | None, str | None]:
    missing = list(map(str, sorted(set_exp - set_ans)))
    missing = f"Missing {item_name}(s): {', '.join(missing)}." if missing else None
    extra = list(map(str, sorted(set_ans - set_exp)))
    extra = f"Found extra {item_name}(s): {', '.join(extra)}." if extra else None
    return missing, extra


def _check_missing_extra(
    ev_ans: Any,
    ev_exp: Any,
    item_name: str,
    getter: callable,
) -> str | None:
    missing_columns, extra_columns = get_items_missing_extra(
        getter(ev_ans), getter(ev_exp), item_name
    )
    if missing_columns or extra_columns:
        return "\n".join(filter(None, [missing_columns, extra_columns]))
    return None


def _check_columns_one_by_one(
    ev_ans: Any,
    ev_exp: Any,
    check_column_values: callable,
    column_names: list[str],
) -> str | None:
    for name in column_names:
        msg = check_column_values(ev_ans[name], ev_exp[name], name)
        if msg is None:
            continue
        return msg


# Questions (Marimo format)
class Question:
    def __init__(self, prompt):
        self.prompt = prompt
        self.correct_answer = None
        self.prefix = ""

    @property
    def answer_name(self):
        return f"{self.prefix}answer"

    @property
    def starting_point(self):
        return f"#Create your answer here!\n{self.answer_name}"

    def show_correct_answer(self):
        return mo.md(self.correct_answer._repr_markdown_())

    def check_answer(self, engine, answer):
        message = check_answer(engine, answer, self.correct_answer)
        return mo.md(f"### {message}")


class DatasetQuestion(Question):
    def __init__(self, prompt):
        super().__init__(prompt)
        self.correct_answer = create_dataset()  # Initial value

    @property
    def answer_name(self):
        return f"{self.prefix}dataset"

    @property
    def starting_point(self):
        return "\n".join(
            [
                f"{self.prefix}dataset = create_dataset()",
                "# Add to the dataset here",
                f"{self.prefix}dataset",
            ]
        )


class TableFilteringQuestion(Question):
    def __init__(self, prompt, table):
        super().__init__(prompt)
        self.table = table
        self.table_name = type(self.table).__name__
        self.correct_answer = table  # Initial value

    @property
    def starting_point(self):
        return "\n".join(
            [
                f"{self.prefix}answer = {self.table_name}",
                "# Filter the table here",
                f"{self.prefix}answer",
            ]
        )


questions = dict()

questions[0] = DatasetQuestion("Create an empty dataset.")

questions[1] = DatasetQuestion(
    "Add column `age` to the dataset corresponding to the patient's age on January 1, 2024."
)
questions[1].correct_answer.age = patients.age_on("2024-01-01")

questions[2] = TableFilteringQuestion(
    "Filter the clinical events table to only include records with SNOMED code `60621009`.",
    clinical_events,
)
questions[2].correct_answer = clinical_events.where(
    clinical_events.snomedct_code.is_in(["60621009"])
)
