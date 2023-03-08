import datetime
import sys

from databuilder.codes import CTV3Code
from databuilder.dummy_data.query_info import ColumnInfo, QueryInfo, TableInfo
from databuilder.ehrql import Dataset, days
from databuilder.query_language import compile
from databuilder.tables import Constraint, EventFrame, PatientFrame, Series, table


@table
class patients(PatientFrame):
    date_of_birth = Series(datetime.date)
    sex = Series(
        str,
        constraints=[
            Constraint.Categorical(
                ["male", "female", "intersex"],
            )
        ],
    )


@table
class events(EventFrame):
    date = Series(datetime.date)
    code = Series(CTV3Code)


def test_query_info_from_variable_definitions():
    dataset = Dataset()
    dataset.set_population(events.exists_for_patient())
    dataset.date_of_birth = patients.date_of_birth
    dataset.sex = patients.sex
    variable_definitions = compile(dataset)

    query_info = QueryInfo.from_variable_definitions(variable_definitions)

    assert query_info == QueryInfo(
        tables={
            "events": TableInfo(
                name="events",
                has_one_row_per_patient=False,
                columns={},
            ),
            "patients": TableInfo(
                name="patients",
                has_one_row_per_patient=True,
                columns={
                    "date_of_birth": ColumnInfo(
                        name="date_of_birth",
                        type=datetime.date,
                    ),
                    "sex": ColumnInfo(
                        name="sex",
                        type=str,
                        constraints=(
                            Constraint.Categorical(
                                values=("male", "female", "intersex")
                            ),
                        ),
                    ),
                },
            ),
        },
        population_table_names=["events"],
        other_table_names=["patients"],
    )


def test_query_info_records_values():
    dataset = Dataset()
    dataset.set_population(events.exists_for_patient())
    # Simple equality comparison
    dataset.q1 = events.where(events.code == CTV3Code("abc00")).exists_for_patient()
    # String contains
    dataset.q2 = patients.sex.contains("ale")
    # Set contains
    dataset.q3 = events.where(
        events.code.is_in([CTV3Code("def00"), CTV3Code("ghi00")])
    ).exists_for_patient()
    # Equality comparison where the column is not selected directly from the table
    old = events.where(events.date < "2000-01-01")
    dataset.q4 = old.sort_by(old.date).first_for_patient().code == CTV3Code("jkl00")

    variable_definitions = compile(dataset)
    query_info = QueryInfo.from_variable_definitions(variable_definitions)
    sex_column_info = query_info.tables["patients"].columns["sex"]
    code_column_info = query_info.tables["events"].columns["code"]

    assert sex_column_info.values_used == {"ale"}
    assert code_column_info.values_used == {"abc00", "def00", "ghi00", "jkl00"}


def test_query_info_ignores_complex_comparisons():
    # By "complex" here we just mean anything other than a direct comparison between a
    # selected column and a static value. We don't attempt to handle these, but we want
    # to make sure we don't blow up with an error, or misinterpret them.
    dataset = Dataset()
    dataset.set_population(events.exists_for_patient())
    dataset.q1 = patients.date_of_birth.year.is_in([2000, 2010, 2020])
    dataset.q2 = patients.date_of_birth + days(100) == "2021-10-20"
    dataset.q3 = patients.date_of_birth == "2022-10-05"
    variable_definitions = compile(dataset)

    query_info = QueryInfo.from_variable_definitions(variable_definitions)
    column_info = query_info.tables["patients"].columns["date_of_birth"]

    assert column_info.values_used == {datetime.date(2022, 10, 5)}


def test_remove_pragmas_for_python_3_10():
    # https://github.com/nedbat/coveragepy/issues/198#issuecomment-798891606
    assert sys.version_info < (3, 10), (
        f"Remove `no cover` pragmas from continue "
        f"statements in {QueryInfo.__module__}"
    )
