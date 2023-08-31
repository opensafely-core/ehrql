In this section, you will write the following dataset definition.
It selects the date and the code of each patient's most recent asthma medication,
for all patients born on or before 31 December 1999.

```python
from ehrql import Dataset
from ehrql.tables.beta.core import patients, medications

dataset = Dataset()

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

## Create an empty dataset definition

From the menu, using **New File...**, create an empty dataset definition called *dataset_definition.py*.

![A screenshot of VS Code, showing an empty dataset definition](empty_dataset_definition.png)

For the remainder of this section,
you should type the code into *dataset_definition.py*.

??? tip "Interact with the code in the sandbox"
    As well as typing the code into *dataset_definition.py*,
    you can interact with the code in the sandbox.
    Remember, when you see `>>>`,
    you should type the code that follows into the sandbox and press ++enter++.

## Import the `Dataset` object

Think of the `Dataset` object as a blueprint for a dataset.

```python
from ehrql import Dataset
```

??? tip "Import the `Dataset` object"
    ```pycon
    >>> from ehrql import Dataset
    ```

## Import the tables

The `patients` table is a patient frame; it has one row per patient.
The `medications` table is an event frame; it has many rows per patient.

```python
from ehrql.tables.beta.core import patients, medications
```

??? tip "Import the tables"
    ```pycon
    >>> from ehrql.tables.beta.core import patients, medications
    ```

## Create the dataset

Create the dataset from the `Dataset` object.

```python
dataset = Dataset()
```

## Define the population

Define the population as all patients born on or before 31 December 1999.

```python
dataset.define_population(patients.date_of_birth.is_on_or_before("1999-12-31"))
```

??? tip "Define the population condition"
    `.define_population` takes a population condition in the form of a boolean patient series.
    However, `patients.date_of_birth` is a date patient series.

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

    To transform a date patient series into a boolean patient series,
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

## Select each patient's most recent asthma medication

Define a list of asthma codes.
**Filter** the `medications` event frame,
so that it contains rows that match the asthma codes on the list.
**Sort** the resulting event frame by date,
so that the most recent asthma medication is the last row for each patient.
From the resulting event frame,
**select** the last row for each patient.
The result is a patient frame that contains each patient's most recent asthma medication.

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

    `medications.dmd_code` is a code event series.

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

    Create a filter condition in the form of a boolean patient series.

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

    **Filter** the `medications` event frame,
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

    **Sort** the resulting event frame by date,
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

    From the resulting event frame,
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

## Add dates and codes to the dataset

Transform the patient frame into two patient series;
one of dates and one of codes.
Add them to the dataset.

```python
dataset.asthma_med_date = latest_asthma_med.date
dataset.asthma_med_code = latest_asthma_med.dmd_code
```

## Save the dataset definition

From the menu, using **File > Save**, save the dataset definition.
