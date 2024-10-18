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
    date_of_birth = random_date(date(1950, 1, 1), TODAY)
    # Round date of birth to the first of the month which reflects what happens in the
    # real data
    date_of_birth = date_of_birth.replace(day=1)

    # You can think of `yield` a bit like `return` except that we can call it multiple
    # times in the same function. This makes it easier for our function to provide data
    # for multiple different tables.
    yield "patients", {"sex": sex, "date_of_birth": date_of_birth}

    # Decide how many medications should our patient be issued
    medications_count = random.randrange(0, 10)

    # Generate data for each of these medication issues
    for _ in range(medications_count):
        meds_date = random_date(date_of_birth, TODAY)
        meds_dmd_code = random.choice(DMD_CODES)
        yield "medications", {"date": meds_date, "dmd_code": meds_dmd_code}


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
