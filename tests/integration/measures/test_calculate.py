import random
from collections import defaultdict
from datetime import date, timedelta
from unittest import mock

import pytest

from ehrql import months, years
from ehrql.measures import INTERVAL, Measures, get_measure_results
from ehrql.measures.calculate import MeasuresTimeout
from ehrql.tables import EventFrame, PatientFrame, Series, table


@table
class patients(PatientFrame):
    sex = Series(str)


@table
class addresses(EventFrame):
    date = Series(date)
    region = Series(str)


@table
class events(EventFrame):
    date = Series(date)
    code = Series(str)
    value = Series(int)


def test_get_measure_results(engine):
    events_in_interval = events.where(events.date.is_during(INTERVAL))
    event_count = events_in_interval.count_for_patient()
    foo_event_count = events_in_interval.where(events.code == "foo").count_for_patient()
    had_event = events_in_interval.exists_for_patient()
    event_value = events_in_interval.value.sum_for_patient()
    region = addresses.sort_by(addresses.date).last_for_patient().region

    intervals = years(3).starting_on("2020-01-01")
    measures = Measures()

    measures.define_measure(
        "foo_events_by_sex",
        numerator=foo_event_count,
        denominator=event_count,
        group_by=dict(sex=patients.sex),
        intervals=intervals,
    )
    measures.define_measure(
        "foo_events_by_region",
        numerator=foo_event_count,
        denominator=event_count,
        group_by=dict(region=region),
        intervals=intervals,
    )
    measures.define_measure(
        "had_event_by_sex",
        numerator=had_event,
        denominator=patients.exists_for_patient(),
        group_by=dict(sex=patients.sex),
        intervals=intervals,
    )
    measures.define_measure(
        "event_value_by_region",
        numerator=event_value,
        denominator=patients.exists_for_patient(),
        group_by=dict(region=region),
        intervals=intervals,
    )
    measures.define_measure(
        "had_event_by_sex_and_region",
        numerator=had_event,
        denominator=patients.exists_for_patient(),
        group_by=dict(
            sex=patients.sex,
            region=region,
        ),
        intervals=intervals,
    )
    measures.define_measure(
        "foo_events",
        numerator=foo_event_count,
        denominator=event_count,
        intervals=intervals,
    )

    patient_data, address_data, event_data = generate_data(intervals)
    engine.populate(
        {patients: patient_data, addresses: address_data, events: event_data}
    )

    results = get_measure_results(engine.query_engine(), measures)
    results = list(results)

    expected = calculate_measure_results(
        intervals, patient_data, address_data, event_data
    )
    expected = list(expected)
    # We don't care about the order of the results
    assert set(results) == set(expected)


@mock.patch("ehrql.measures.calculate.time")
def test_get_measure_results_with_timeout(patched_time, in_memory_engine):
    events_in_interval = events.where(events.date.is_during(INTERVAL))
    event_count = events_in_interval.count_for_patient()
    foo_event_count = events_in_interval.where(events.code == "foo").count_for_patient()

    intervals = months(60).starting_on("2000-01-01")
    measures = Measures()

    measures.define_measure(
        "foo_events",
        numerator=foo_event_count,
        denominator=event_count,
        intervals=intervals,
        group_by=dict(
            sex=patients.sex,
        ),
    )

    patient_data, _, event_data = generate_data(intervals)
    in_memory_engine.populate({patients: patient_data, events: event_data})

    patched_time.time.side_effect = [0.0, 1000.0, 1000000.0]
    results = get_measure_results(in_memory_engine.query_engine(), measures)
    with pytest.raises(MeasuresTimeout, match="time limit"):
        results = list(results)


def generate_data(intervals):
    rnd = random.Random(20230518)
    # Generate some random patients
    patient_data = [
        dict(
            patient_id=patient_id,
            sex=rnd.choice(["male", "female"]),
        )
        for patient_id in range(1, 50)
    ]
    # Generate some addresses (at least one) for each patient
    address_data = []
    interval_range = (intervals[0][0], intervals[-1][1])
    for patient in patient_data:
        for _ in range(rnd.randint(1, 3)):
            address_data.append(
                dict(
                    patient_id=patient["patient_id"],
                    date=random_date_in_interval(rnd, interval_range),
                    region=rnd.choice(["London", "The North", "The Countryside"]),
                )
            )
    # For each interval and patient, generate some events (possibly zero)
    event_data = []
    for interval in intervals:
        for patient in patient_data:
            # Choose a number of events, biased towards zero
            event_count = max(rnd.randint(-10, 10), 0)
            event_data.extend(
                dict(
                    patient_id=patient["patient_id"],
                    code=rnd.choice(["abc", "def", "foo"]),
                    date=random_date_in_interval(rnd, interval),
                    value=rnd.randint(0, 10),
                )
                for _ in range(event_count)
            )
    return patient_data, address_data, event_data


def random_date_in_interval(rnd, interval):
    days_in_interval = (interval[1] - interval[0]).days
    offset = rnd.randint(0, days_in_interval)
    return interval[0] + timedelta(days=offset)


def calculate_measure_results(intervals, patient_data, address_data, event_data):
    nums = defaultdict(int)
    dens = defaultdict(int)

    for interval, patient, address, events in group_events(
        intervals, patient_data, address_data, event_data
    ):
        event_count = len(events)
        foo_count = len([e for e in events if e["code"] == "foo"])
        had_event = 1 if events else 0
        event_value = sum([e["value"] for e in events], start=0)

        nums[("foo_events_by_sex", interval, patient["sex"], None)] += foo_count
        dens[("foo_events_by_sex", interval, patient["sex"], None)] += event_count
        nums[("foo_events_by_region", interval, None, address["region"])] += foo_count
        dens[("foo_events_by_region", interval, None, address["region"])] += event_count
        nums[("had_event_by_sex", interval, patient["sex"], None)] += had_event
        dens[("had_event_by_sex", interval, patient["sex"], None)] += 1
        nums[("event_value_by_region", interval, None, address["region"])] += (
            event_value
        )
        dens[("event_value_by_region", interval, None, address["region"])] += 1
        nums[
            ("had_event_by_sex_and_region", interval, patient["sex"], address["region"])
        ] += had_event
        dens[
            ("had_event_by_sex_and_region", interval, patient["sex"], address["region"])
        ] += 1
        nums[("foo_events", interval, None, None)] += foo_count
        dens[("foo_events", interval, None, None)] += event_count

    for key, numerator in nums.items():
        measure, interval, sex, region = key
        denominator = dens[key]
        ratio = numerator / denominator
        yield (
            measure,
            interval[0],
            interval[1],
            ratio,
            numerator,
            denominator,
            sex,
            region,
        )


def group_events(intervals, patient_data, address_data, event_data):
    "Group events by interval and patient"
    for patient in patient_data:
        patient_events = [
            e for e in event_data if e["patient_id"] == patient["patient_id"]
        ]
        patient_addresses = sorted(
            [a for a in address_data if a["patient_id"] == patient["patient_id"]],
            key=lambda a: a["date"],
        )
        address = patient_addresses[-1]
        for interval in intervals:
            interval_events = [
                e for e in patient_events if interval[0] <= e["date"] <= interval[1]
            ]
            yield interval, patient, address, interval_events
