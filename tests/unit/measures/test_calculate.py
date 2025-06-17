from datetime import date

from ehrql import INTERVAL, create_measures, months
from ehrql.measures import get_column_specs_for_measures, get_table_specs_for_measures
from ehrql.measures.calculate import (
    combine_measure_tables_as_results,
    split_measure_results_into_tables,
)
from ehrql.tables.core import clinical_events, patients


def get_measures_and_results():
    events = clinical_events.where(clinical_events.date.is_during(INTERVAL))
    age_band = (patients.age_on(INTERVAL.start_date) // 10) * 10

    measures = create_measures()
    measures.define_defaults(
        numerator=events.count_for_patient(),
        denominator=events.exists_for_patient(),
        intervals=months(2).starting_on("2020-01-01"),
    )
    measures.define_measure(
        "a",
        group_by={"age_band": age_band},
    )
    measures.define_measure(
        "b",
        group_by={"sex": patients.sex},
    )
    measures.define_measure(
        "c",
        group_by={
            "age_band": age_band,
            "is_alive": patients.is_alive_on(INTERVAL.start_date),
        },
    )

    # Note that these results aren't intended to be complete
    results = [
        # measure, interval_start, interval_end, ratio, numerator, denominator, age_band, sex, is_alive
        ("a", date(2020, 1, 1), date(2020, 1, 31), 0.5, 1, 2, 10, None, None),
        ("b", date(2020, 1, 1), date(2020, 1, 31), 0.5, 1, 2, None, "male", None),
        ("c", date(2020, 1, 1), date(2020, 1, 31), 0.5, 1, 2, 50, None, False),
        ("a", date(2020, 1, 1), date(2020, 1, 31), 2.5, 5, 2, 20, None, None),
        ("c", date(2020, 1, 1), date(2020, 1, 31), 2.5, 5, 2, 60, None, True),
        ("b", date(2020, 1, 1), date(2020, 1, 31), 2.5, 5, 2, None, "female", None),
    ]

    return measures, results


def test_split_measure_results_into_tables():
    measures, results = get_measures_and_results()

    column_specs = get_column_specs_for_measures(measures)
    table_specs = get_table_specs_for_measures(measures)
    tables = split_measure_results_into_tables(results, column_specs, table_specs)

    assert tables == [
        # measure a
        [
            # interval_start, interval_end, ratio, numerator, denominator, age_band
            (date(2020, 1, 1), date(2020, 1, 31), 0.5, 1, 2, 10),
            (date(2020, 1, 1), date(2020, 1, 31), 2.5, 5, 2, 20),
        ],
        # measure b
        [
            # interval_start, interval_end, ratio, numerator, denominator, sex
            (date(2020, 1, 1), date(2020, 1, 31), 0.5, 1, 2, "male"),
            (date(2020, 1, 1), date(2020, 1, 31), 2.5, 5, 2, "female"),
        ],
        # measure c
        [
            # interval_start, interval_end, ratio, numerator, denominator, age_band, is_alive
            (date(2020, 1, 1), date(2020, 1, 31), 0.5, 1, 2, 50, False),
            (date(2020, 1, 1), date(2020, 1, 31), 2.5, 5, 2, 60, True),
        ],
    ]


def test_combine_measure_tables_as_results():
    measures, results = get_measures_and_results()

    # Split the single results list into multiple tables
    column_specs = get_column_specs_for_measures(measures)
    table_specs = get_table_specs_for_measures(measures)
    tables = split_measure_results_into_tables(results, column_specs, table_specs)

    # Combine the tables back into a single results list
    roundtrip_results = combine_measure_tables_as_results(
        tables, column_specs, table_specs
    )
    roundtrip_results = list(roundtrip_results)

    # Check that we're back where we started (modulo row order)
    assert len(results) == len(roundtrip_results)
    assert set(results) == set(roundtrip_results)
