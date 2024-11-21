#!/usr/bin/env python
"""
Generates a directory of CSV files containing example data for the ehrQL sandbox
"""

import argparse
import csv
import random
from collections import defaultdict
from datetime import date
from pathlib import Path


# This ensures we generate the same random data each time the script is run
random.seed("123456789")

# We use a fixed date for "today" so that we always generate the same data regardless of
# which day we run the script on.
TODAY = date(2024, 10, 1)

# Ten 5-digit practice id's
PRACTICE_PSEUDO_IDS = [
    "70448",
    "23938",
    "79119",
    "79802",
    "30634",
    "54030",
    "35838",
    "66836",
    "84732",
    "73948",
]

# Clinical event codes
DIABETES_CODE = 111552007
DIABETES_RESOLVED_CODE = 315051004
MILD_FRAILTY_CODE = 925791000000100
MODERATE_FRAILTY_CODE = 925831000000107
SEVERE_FRAILTY_CODE = 925861000000102
HBA1C_CODE = 999791000000106
NEPHROPATHY_CODE = 29738008
MICROALBUMINURIA_CODE = 312975006
STRUCTED_EDUCATION_PROGRAMME_CODE = 415270003

# Prescription codes
ACE_CODE = 29984111000001107
ARB_CODE = 34188411000001109

# Clinical event date
earliest_event = date(2022, 4, 1)
latest_event = date(2024, 3, 31)


def main(output_directory):
    # We're going to generate rows of data which we want to group together by the table
    # they belong to. So we're going to construct a dictionary which has the shape:
    #
    #     {
    #         <table_name_1>: [<data_for_row_1>, <data_for_row_2>, ... ],
    #         <table_name_2>: [<data_for_row_1>, <data_for_row_2>, ... ],
    #         ...
    #     }
    #
    # Using `defaultdict(list)` means we automatically get an empty list to append to
    # for each table name the first time we use it, which makes the code simpler.
    rows_by_table = defaultdict(list)

    # Generate a fixed list of patient IDs
    for patient_id in range(1, 101):
        # For each patient, generate some data which will be spread over several
        # different tables
        for table_name, row in generate_patient_data():
            # Add the appropriate patient ID to each row of data
            row_with_id = {"patient_id": patient_id} | row
            # Then add the row to list of rows for the appropriate table
            rows_by_table[table_name].append(row_with_id)

    # Finally, write the data to disk
    write_data(output_directory, rows_by_table)


def generate_patient_data():
    # Generate some random data for our patient
    sex = random.choice(["male", "female"])

    # ensure that approximately 90 patients are alive
    is_dead = random.choices([True, False], weights=[10, 90], k=1)[0]

    date_of_birth = random_date(date(1950, 1, 1), TODAY)
    # Round date of birth to the first of the month which reflects what happens in the
    # real data
    date_of_birth = date_of_birth.replace(day=1)

    if is_dead:
        date_of_death = random_date(date_of_birth, TODAY)
    else:
        date_of_death = None

    # You can think of `yield` a bit like `return` except that we can call it multiple
    # times in the same function. This makes it easier for our function to provide data
    # for multiple different tables.
    yield (
        "patients",
        {"sex": sex, "date_of_birth": date_of_birth, "date_of_death": date_of_death},
    )

    # Create patient practice registration history: set the max number of registrations per patient
    registrations_count = random.randrange(1, 11)

    # generate data for registrations
    generated_dates = []
    for _ in range(registrations_count):
        practice_pseudo_id = random.choice(PRACTICE_PSEUDO_IDS)
        if is_dead:
            last_possible_date = date_of_death
        else:
            last_possible_date = TODAY

        while True:
            start_date = random_date(date_of_birth, last_possible_date)
            end_date = random_date(start_date, last_possible_date)

            if not date_overlap_repeat(start_date, end_date, generated_dates):
                generated_dates.append((start_date, end_date))
                yield (
                    "practice_registrations",
                    {
                        "start_date": start_date,
                        "end_date": end_date,
                        "practice_pseudo_id": practice_pseudo_id,
                    },
                )
                break

    # Generate data for medications
    if is_dead:
        earliest_possible_event = date_of_birth
        last_possible_event = date_of_death
    else:
        earliest_possible_event = earliest_event
        last_possible_event = latest_event

    # ARB
    yield from assign_patient_medication(
        10, ARB_CODE, earliest_possible_event, last_possible_event
    )

    # ACE-I
    yield from assign_patient_medication(
        10, ACE_CODE, earliest_possible_event, last_possible_event
    )

    # Generate clinical events for patients = DIABETES
    diabetes_number = random.choice(range(1, 101))
    if diabetes_number <= 85:
        # patient has a diabetes diagnosis code
        date0 = random_date(earliest_possible_event, last_possible_event)

        yield (
            "clinical_events",
            {
                "date": date0,
                "snomedct_code": DIABETES_CODE,
                "numeric_value": "",
            },
        )

    if 75 < diabetes_number <= 85:
        # patient has a diabetes diagnosis code followed by a diabetes resolved code
        date2 = random_date(date0, last_possible_event)

        yield (
            "clinical_events",
            {
                "date": date2,
                "snomedct_code": DIABETES_RESOLVED_CODE,
                "numeric_value": "",
            },
        )

    if 80 < diabetes_number <= 85:
        # patient has a diabetes diagnosis code followed by a diabetes resolved code, followed by another diagnosis code
        date3 = random_date(date2, last_possible_event)

        yield (
            "clinical_events",
            {
                "date": date3,
                "snomedct_code": DIABETES_CODE,
                "numeric_value": "",
            },
        )

    # Generate clinical events for patients = FRAILTY
    frailty_number = random.choice(range(1, 101))
    if frailty_number <= 10:
        # patient has severe frailty
        date4 = random_date(earliest_possible_event, last_possible_event)

        yield (
            "clinical_events",
            {
                "date": date4,
                "snomedct_code": SEVERE_FRAILTY_CODE,
                "numeric_value": "",
            },
        )

    elif 10 < frailty_number <= 20:
        # patient has moderate frailty
        date5 = random_date(earliest_possible_event, last_possible_event)

        yield (
            "clinical_events",
            {
                "date": date5,
                "snomedct_code": MODERATE_FRAILTY_CODE,
                "numeric_value": "",
            },
        )

    elif 20 < frailty_number <= 25:
        # patient was diagnosed with mild frailty and later with moderate frailty
        date6 = random_date(earliest_possible_event, last_possible_event)
        date7 = random_date(date6, last_possible_event)

        yield (
            "clinical_events",
            {
                "date": date6,
                "snomedct_code": MILD_FRAILTY_CODE,
                "numeric_value": "",
            },
        )
        yield (
            "clinical_events",
            {
                "date": date7,
                "snomedct_code": MODERATE_FRAILTY_CODE,
                "numeric_value": "",
            },
        )

    elif 25 < frailty_number <= 30:
        # patient was diagnosed with moderate frailty and later with mild frailty
        date8 = random_date(earliest_possible_event, last_possible_event)
        date9 = random_date(date8, last_possible_event)

        yield (
            "clinical_events",
            {
                "date": date8,
                "snomedct_code": MODERATE_FRAILTY_CODE,
                "numeric_value": "",
            },
        )
        yield (
            "clinical_events",
            {
                "date": date9,
                "snomedct_code": MILD_FRAILTY_CODE,
                "numeric_value": "",
            },
        )

    # Generate clinical events for patients = HBA1C
    hba_number = random.choice(range(1, 101))
    low = random.choice(range(38, 59))
    high = random.choice(range(58, 79))

    if hba_number <= 20:
        # patient has low HbA1c value
        date11 = random_date(earliest_possible_event, last_possible_event)
        hba1c_1 = low
        yield (
            "clinical_events",
            {
                "date": date11,
                "snomedct_code": HBA1C_CODE,
                "numeric_value": hba1c_1,
            },
        )
    elif 20 < hba_number <= 40:
        # patient has high HbA1c value
        date12 = random_date(earliest_possible_event, last_possible_event)
        hba1c_2 = high
        yield (
            "clinical_events",
            {
                "date": date12,
                "snomedct_code": HBA1C_CODE,
                "numeric_value": hba1c_2,
            },
        )
    elif 40 < hba_number <= 50:
        # patient has low HbA1c value followed by high hba1c value
        date13 = random_date(earliest_possible_event, last_possible_event)
        date14 = random_date(date13, last_possible_event)
        hba1c_3 = low
        hba1c_4 = high
        yield (
            "clinical_events",
            {
                "date": date13,
                "snomedct_code": HBA1C_CODE,
                "numeric_value": hba1c_3,
            },
        )
        yield (
            "clinical_events",
            {
                "date": date14,
                "snomedct_code": HBA1C_CODE,
                "numeric_value": hba1c_4,
            },
        )
    elif 50 < hba_number <= 60:
        # patient has high HbA1c value followed by low hba1c value
        date15 = random_date(earliest_possible_event, last_possible_event)
        date16 = random_date(date15, last_possible_event)
        hba1c_5 = high
        hba1c_6 = low
        yield (
            "clinical_events",
            {
                "date": date15,
                "snomedct_code": HBA1C_CODE,
                "numeric_value": hba1c_5,
            },
        )
        yield (
            "clinical_events",
            {
                "date": date16,
                "snomedct_code": HBA1C_CODE,
                "numeric_value": hba1c_6,
            },
        )

    # nephropathy
    yield from assign_patient_event(
        10, NEPHROPATHY_CODE, earliest_possible_event, last_possible_event
    )

    # micro-albuminuria
    yield from assign_patient_event(
        10, MICROALBUMINURIA_CODE, earliest_possible_event, last_possible_event
    )

    # structured education programme
    yield from assign_patient_event(
        20,
        STRUCTED_EDUCATION_PROGRAMME_CODE,
        earliest_possible_event,
        last_possible_event,
    )


def assign_patient_medication(
    frequency: int, prescription_code, earliest_possible_event, last_possible_event
):
    random_number = random.choice(range(1, 101))
    if random_number in range(1, frequency + 1):
        date18 = random_date(earliest_possible_event, last_possible_event)
        yield (
            "medications",
            {
                "date": date18,
                "dmd_code": prescription_code,
            },
        )


def assign_patient_event(
    frequency: int, event_code, earliest_possible_event, last_possible_event
):
    random_number = random.choice(range(1, 101))
    if random_number in range(1, frequency + 1):
        date17 = random_date(earliest_possible_event, last_possible_event)
        yield (
            "clinical_events",
            {
                "date": date17,
                "snomedct_code": event_code,
                "numeric_value": "",
            },
        )


# check for overlap and repeat
def date_overlap_repeat(start_date, end_date, generated_dates):
    """
    Checks for overlapping and repeated date ranges. Example cases
    #1 if existing_start = 2024-03-31, existing_end = 2024-08-11, start_date = 2024-08-14, end_date = 2024-09-02
    This will return False   i.e. there is no overlap
    #2 if existing_start = 2024-03-31, existing_end = 2024-08-11, start_date = 2024-01-26, end_date = 2024-06-23
    This will return True    i.e. there is an overlap
    #3 if existing_start = 2024-03-31, existing_end = 2024-08-11, start_date = 2024-01-25, end_date = 2024-10-29
    This will return True    i.e. there is an overlap
    #4 if existing_start = 2024-03-31, existing_end = 2024-08-11, start_date = 2024-03-31, end_date = 2024-08-11
    This will return True    i.e. it is repeated
    """
    for existing_start, existing_end in generated_dates:
        # check overlap
        if start_date < existing_end and end_date > existing_start:
            return True
        # check repeat
        if start_date == existing_start and end_date == existing_end:
            return True
    return False


def random_date(earliest, latest):
    "Generate a random date between two dates"
    # Calculate the span of time between the two dates
    span = latest - earliest
    # `random.random()` gives us a number between 0.0 and 1.0 which we can use to get a
    # random proportion of this span
    offset = span * random.random()
    # Add the random offset back to the earliest date to give us a new date
    return earliest + offset


def write_data(output_directory, rows_by_table):
    # Create the output directory if it doesn't exist already
    output_directory = Path(output_directory)

    # Create sub-directory
    example_directory = output_directory / "example-data"
    example_directory.mkdir(parents=True, exist_ok=True)
    # For each table, write its data to a CSV file in the output directory
    for table_name, rows in rows_by_table.items():
        write_data_for_table(example_directory, table_name, rows)


def write_data_for_table(example_directory, table_name, rows):
    filename = example_directory / f"{table_name}.csv"
    # Here the `w` means that we're opening the file to write to it, and the `newline`
    # argument is just "one of those things" we need to reliably format CSV
    with filename.open("w", newline="") as f:
        # Use the first row of data to find out what headers the CSV file needs
        headers = rows[0].keys()
        # Write those headers out
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        # Write all the rows of data to the file
        for row in rows:
            writer.writerow(row)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output_directory", type=Path)
    kwargs = vars(parser.parse_args())
    main(**kwargs)
