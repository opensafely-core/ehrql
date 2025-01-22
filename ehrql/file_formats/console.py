"""
Handles writing rows/tables to the console for local development and debugging.

At present, this just uses the CSV writer but there's scope for using something a bit
prettier and more readable here in future.
"""

import sys

from ehrql.file_formats.csv import write_rows_csv_lines


def write_rows_console(rows, column_specs):
    write_rows_csv_lines(sys.stdout, rows, column_specs)


def write_tables_console(tables, table_specs):
    write_table_names = len(table_specs) > 1
    first_table = True
    for rows, (table_name, column_specs) in zip(tables, table_specs.items()):
        if first_table:
            first_table = False
        else:
            # Add whitespace between tables
            sys.stdout.write("\n\n")
        if write_table_names:
            sys.stdout.write(f"{table_name}\n")
        write_rows_console(rows, column_specs)
