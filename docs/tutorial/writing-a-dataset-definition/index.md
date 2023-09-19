In this section, you will write the following dataset definition.
It selects the date and the code of each patient's most recent asthma medication,
for all patients born on or before 31 December 1999.

```python
from ehrql import create_dataset
from ehrql.tables.beta.core import patients, medications

dataset = create_dataset()

dataset.define_population(patients.date_of_birth.is_on_or_before("1999-12-31"))

asthma_codes = ["39113311000001107", "39113611000001102"]
latest_asthma_med = (
    medications.where(medications.dmd_code.is_in(asthma_codes))
    .sort_by(medications.date)
    .last_for_patient()
)

dataset.asthma_med_date = latest_asthma_med.date
dataset.asthma_med_code = latest_asthma_med.dmd_code
```

## Open the dataset definition

1. Click *dataset_definition.py* in the **Explorer** towards the top left of the codespace

![A screenshot of VS Code, showing an empty dataset definition](empty_dataset_definition.png)

For the remainder of this section,
you should type the code into *dataset_definition.py*.

??? tip "Interact with the code in the sandbox"
    As well as typing the code into *dataset_definition.py*,
    you can interact with the code in the sandbox.
    Remember, when you see `>>>`,
    you should type the code that follows into the sandbox and press ++enter++.

## Import the `create_dataset` function

```python
from ehrql import create_dataset
```

??? tip "Import the `create_dataset` function"
    ```pycon
    >>> from ehrql import create_dataset
    ```

## Import the tables

The `patients` table has one row per patient.
The `medications` table has many rows per patient.

```python
from ehrql.tables.beta.core import patients, medications
```

??? tip "Import the tables"
    ```pycon
    >>> from ehrql.tables.beta.core import patients, medications
    ```

## Create the dataset

```python
dataset = create_dataset()
```

??? tip "Create the dataset"
    ```pycon
    >>> dataset = create_dataset()
    >>> dataset
    Dataset()
    ```

## Define the population

Define the population as all patients born on or before 31 December 1999.

```python
dataset.define_population(patients.date_of_birth.is_on_or_before("1999-12-31"))
```

??? tip "Define the population"
    `.define_population` takes a population condition in the form of a boolean column.
    However, `patients.date_of_birth` is a date column.

    ```pycon
    >>> patients.date_of_birth
    0 | 1973-07-01
    1 | 1948-03-01
    2 | 2003-04-01
    3 | 2007-06-01
    4 | 1938-10-01
    5 | 1994-04-01
    6 | 1953-05-01
    7 | 1992-08-01
    8 | 1931-10-01
    9 | 1979-04-01
    ```

    To transform a date column into a boolean column,
    use `.is_on_or_before` with a date.

    ```pycon
    >>> patients.date_of_birth.is_on_or_before("1999-12-31")
    0 | True
    1 | True
    2 | False
    3 | False
    4 | True
    5 | True
    6 | True
    7 | True
    8 | True
    9 | True
    ```

    Compare the patients in the boolean column with the patients in the dataset,
    after defining the population.

    ```pycon
    >>> dataset.define_population(patients.date_of_birth.is_on_or_before("1999-12-31"))
    >>> dataset
    patient_id
    -----------------
    0
    1
    4
    5
    6
    7
    8
    9
    ```

    Notice that patients with `True` in the boolean column are included in the population;
    and patients with `False` in the boolean column are excluded from the population.

## Select each patient's most recent asthma medication

Define a list of asthma codes.
**Filter** the `medications` table,
so that it contains rows that match the asthma codes on the list.
**Sort** the resulting table by date,
so that the most recent asthma medication is the last row for each patient.
From the resulting table,
**select** the last row for each patient.
The result is a table that contains each patient's most recent asthma medication.

```python
asthma_codes = ["39113311000001107", "39113611000001102"]
latest_asthma_med = (
    medications.where(medications.dmd_code.is_in(asthma_codes))
    .sort_by(medications.date)
    .last_for_patient()
)
```

??? tip "Unpack the filter, the sort, and the select"
    Define a list of asthma codes.

    ```pycon
    >>> asthma_codes = ["39113311000001107", "39113611000001102"]
    ```

    `medications.dmd_code` is a code column.

    ```pycon
    >>> medications.dmd_code
    0 | 0 | 39113611000001102
    1 | 1 | 39113611000001102
    1 | 2 | 39113311000001107
    1 | 3 | 22777311000001105
    3 | 4 | 22777311000001105
    4 | 5 | 39113611000001102
    5 | 6 | 3484711000001105
    5 | 7 | 39113611000001102
    7 | 8 | 3484711000001105
    9 | 9 | 3484711000001105
    ```

    Create a filter condition in the form of a boolean column.

    ```pycon
    >>> medications.dmd_code.is_in(asthma_codes)
    0 | 0 | True
    1 | 1 | True
    1 | 2 | True
    1 | 3 | False
    3 | 4 | False
    4 | 5 | True
    5 | 6 | False
    5 | 7 | True
    7 | 8 | False
    9 | 9 | False
    ```

    **Filter** the `medications` table,
    so that it contains rows that match the asthma codes on the list.

    ```pycon
    >>> medications.where(medications.dmd_code.is_in(asthma_codes))
    patient_id        | row_id            | date              | dmd_code
    ------------------+-------------------+-------------------+------------------
    0                 | 0                 | 2014-01-11        | 39113611000001102
    1                 | 1                 | 2015-08-06        | 39113611000001102
    1                 | 2                 | 2018-09-21        | 39113311000001107
    4                 | 5                 | 2017-05-11        | 39113611000001102
    5                 | 7                 | 2019-07-06        | 39113611000001102
    ```

    **Sort** the resulting table by date,
    so that the most recent asthma medication is the last row for each patient.

    ```pycon
    >>> medications.where(medications.dmd_code.is_in(asthma_codes)).sort_by(medications.date)
    patient_id        | row_id            | date              | dmd_code
    ------------------+-------------------+-------------------+------------------
    0                 | 0                 | 2014-01-11        | 39113611000001102
    1                 | 1                 | 2015-08-06        | 39113611000001102
    1                 | 2                 | 2018-09-21        | 39113311000001107
    4                 | 5                 | 2017-05-11        | 39113611000001102
    5                 | 7                 | 2019-07-06        | 39113611000001102
    ```

    From the resulting table,
    **select** the last row for each patient.

    ```pycon
    >>> medications.where(medications.dmd_code.is_in(asthma_codes)).sort_by(medications.date).last_for_patient()
    patient_id        | date              | dmd_code
    ------------------+-------------------+------------------
    0                 | 2014-01-11        | 39113611000001102
    1                 | 2018-09-21        | 39113311000001107
    4                 | 2017-05-11        | 39113611000001102
    5                 | 2019-07-06        | 39113611000001102
    ```

## Add the date column to the dataset

Select the date column and add it to the dataset.

```python
dataset.asthma_med_date = latest_asthma_med.date
```

??? tip "Add the date column to the dataset"
    ```pycon
    >>> dataset.asthma_med_date = latest_asthma_med.date
    >>> dataset
    patient_id        | asthma_med_date
    ------------------+------------------
    0                 | 2014-01-11
    1                 | 2018-09-21
    4                 | 2017-05-11
    5                 | 2019-07-06
    6                 | None
    7                 | None
    8                 | None
    9                 | None
    ```

## Add the code column to the dataset

Select the code column and add it to the dataset.

```python
dataset.asthma_med_code = latest_asthma_med.dmd_code
```

??? tip "Add the code column to the dataset"
    ```pycon
    >>> dataset.asthma_med_code = latest_asthma_med.dmd_code
    >>> dataset
    patient_id        | asthma_med_date   | asthma_med_code
    ------------------+-------------------+------------------
    0                 | 2014-01-11        | 39113611000001102
    1                 | 2018-09-21        | 39113311000001107
    4                 | 2017-05-11        | 39113611000001102
    5                 | 2019-07-06        | 39113611000001102
    6                 | None              | None
    7                 | None              | None
    8                 | None              | None
    9                 | None              | None
    ```

## Save the dataset definition

1. Click the menu icon towards the top left of the codespace

    ![VS Code's menu icon](menu_icon.png){ width=50 }

1. Click **File > Save**
