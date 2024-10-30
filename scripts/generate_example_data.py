#!/usr/bin/env python
"""
Generates a directory of CSV files containing example data for the ehrQL sandbox
"""

import argparse
import csv
import pathlib
import random
from collections import defaultdict
from datetime import date


# This ensures we generate the same random data each time the script is run
random.seed("123456789")

# We use a fixed date for "today" so that we always generate the same data regardless of
# which day we run the script on.
TODAY = date(2024, 10, 1)

# A small selection of dm+d codes – we can expand this in future
DMD_CODES = [
    "3408611000001107",
    "3382711000001107",
    "3293111000001105",
    "35937211000001107",
]

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


def main(output_dir):
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
    for patient_id in range(1, 100):
        # For each patient, generate some data which will be spread over several
        # different tables
        for table_name, row in generate_patient_data():
            # Add the appropriate patient ID to each row of data
            row_with_id = {"patient_id": patient_id} | row
            # Then add the row to list of rows for the appropriate table
            rows_by_table[table_name].append(row_with_id)

    # Finally, write the data to disk
    write_data(output_dir, rows_by_table)


def generate_patient_data():
    # Generate some random data for our patient
    sex = random.choice(["male", "female"])
    is_dead = random.choice([True, False])
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

    # Decide how many medications should our patient be issued
    medications_count = random.randrange(0, 10)

    # Generate data for each of these medication issues
    for _ in range(medications_count):
        if is_dead:
            meds_date = random_date(date_of_birth, date_of_death)
        else:
            meds_date = random_date(date_of_birth, TODAY)
        meds_dmd_code = random.choice(DMD_CODES)
        yield "medications", {"date": meds_date, "dmd_code": meds_dmd_code}

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
                        "practice_id": practice_pseudo_id,
                    },
                )
                break


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


def write_data(output_dir, rows_by_table):
    # Create the output directory if it doesn't exist already
    output_dir.mkdir(exist_ok=True)
    # For each table, write its data to a CSV file in the output directory
    for table_name, rows in rows_by_table.items():
        write_data_for_table(output_dir, table_name, rows)


def write_data_for_table(output_dir, table_name, rows):
    filename = output_dir / f"{table_name}.csv"
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
    parser.add_argument("output_dir", type=pathlib.Path)
    kwargs = vars(parser.parse_args())
    main(**kwargs)
