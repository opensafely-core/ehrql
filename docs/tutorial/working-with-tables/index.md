In this section, you will work with tables in the sandbox.

## Start the sandbox

In the terminal, type

```
opensafely exec ehrql:v0 sandbox example-data
```

and press ++enter++.

![A screenshot of VS Code, showing the sandbox](the_sandbox.png)

Notice that the *command prompt*,
or the set of characters before the cursor,
has changed to `>>>`.
For the remainder of this section,
when you see `>>>`,
you should type the code that follows into the sandbox and press ++enter++.

## Work with patient data

In most cases, there is one source of patient data: the `patients` table.
To work with the `patients` table,
first import it into the sandbox.

```pycon
'includes/code/tutorial/working-with-frames-and-series/frames_sandbox-pycon-success/session.txt:patients_import'
```

The `patients` table has one row per patient.
Notice that all values in the `patient_id` column are unique.

```pycon
--8<-- 'includes/code/tutorial/working-with-frames-and-series/frames_sandbox-pycon-success/session.txt:patients_table'
```

Similarly, the `patients.date_of_birth` column has one row per patient.
(If a table has one row per patient, then a column from the table must also have one row per patient.)
Notice that the column is indexed by `patient_id`.

```pycon
--8<-- 'includes/code/tutorial/working-with-frames-and-series/frames_sandbox-pycon-success/session.txt:patients_dob'
```

## Work with event data

Unlike patient data, there are many sources of event data:
the `medications` table, for example.
To work with the `medications` table,
first import it into the sandbox.

```pycon
--8<-- 'includes/code/tutorial/working-with-frames-and-series/frames_sandbox-pycon-success/session.txt:medications_import'
```

The `medications` table has many rows per patient.
Notice that some values in the `patient_id` column are not unique,
but that all values in the `row_id` column are unique.

```pycon
--8<-- 'includes/code/tutorial/working-with-frames-and-series/frames_sandbox-pycon-success/session.txt:medications_table'
```

Similarly, the `medications.date` column has many rows per patient.
Notice that the column is indexed by `patient_id` and `row_id`.

```pycon
--8<-- 'includes/code/tutorial/working-with-frames-and-series/frames_sandbox-pycon-success/session.txt:medications_date'
```

## Transform tables into a dataset

Your task, as a researcher, is to transform tables
— such as `patients` and `medications` —
into a dataset that is suitable for analysis.

??? tip "Tables and datasets"
    In ehrQL, **tables and datasets perform different functions**.
    Whilst both can be represented as rows and columns,
    a *dataset* is a group of patients with common statistical characteristics.
    In other words, a *dataset* is a *cohort*.

### Transform event data into patient data

To transform event data into patient data:

1. Sort the event data
2. Select either the first row or the last row of the event data

```pycon
--8<-- 'includes/code/tutorial/working-with-frames-and-series/frames_sandbox-pycon-success/session.txt:first_medication'
```

### Filter event data

To filter event data,
select rows that match or do not match a condition.

Rows that match 100mcg/dose Salbutamol:

```pycon
--8<-- 'includes/code/tutorial/working-with-frames-and-series/frames_sandbox-pycon-success/session.txt:medications_dmd'
```

Rows that do not match 100mcg/dose Salbutamol:

```pycon
--8<-- 'includes/code/tutorial/working-with-frames-and-series/frames_sandbox-pycon-success/session.txt:medications_except'
```

### Extract a column of years from a column of dates

To extract a column of years from a column of dates,
append `.year` to the column of dates.

```pycon
--8<-- 'includes/code/tutorial/working-with-frames-and-series/frames_sandbox-pycon-success/session.txt:patients_year'
```

### Add one or more years to a column of dates

To add one or more years to a column of dates,
use the `years` function.

```pycon
--8<-- 'includes/code/tutorial/working-with-frames-and-series/frames_sandbox-pycon-success/session.txt:ehrql_years'
```
