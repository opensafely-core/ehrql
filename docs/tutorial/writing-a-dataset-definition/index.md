In this section, you will write the following dataset definition.
It selects the date and the code of each patient's most recent asthma medication,
for all patients born on or before 31 December 1999.

```python
--8<-- 'includes/code/tutorial/writing-a-dataset-definition/asthma_medications-standalone-success/analysis/dataset_definition.py:dataset_definition'
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

## Import the `Dataset` object

Think of the `Dataset` object as a blueprint for a dataset.

```python
--8<-- 'includes/code/tutorial/writing-a-dataset-definition/asthma_medications-standalone-success/analysis/dataset_definition.py:dataset_import'
```

??? tip "Import the `Dataset` object"
    ```pycon
    --8<-- 'includes/code/tutorial/writing-a-dataset-definition/asthma_medications-pycon-success/session.txt:dataset_import'
    ```

## Import the tables

The `patients` table has one row per patient.
The `medications` table has many rows per patient.

```python
--8<-- 'includes/code/tutorial/writing-a-dataset-definition/asthma_medications-standalone-success/analysis/dataset_definition.py:tables_import'
```

??? tip "Import the tables"
    ```pycon
    --8<-- 'includes/code/tutorial/writing-a-dataset-definition/asthma_medications-pycon-success/session.txt:tables_import'
    ```

## Create the dataset

Create the dataset from the `Dataset` object.

```python
--8<-- 'includes/code/tutorial/writing-a-dataset-definition/asthma_medications-standalone-success/analysis/dataset_definition.py:dataset_object'
```

## Define the population

Define the population as all patients born on or before 31 December 1999.

```python
--8<-- 'includes/code/tutorial/writing-a-dataset-definition/asthma_medications-standalone-success/analysis/dataset_definition.py:define_population'
```

??? tip "Define the population condition"

    `.define_population` takes a population condition in the form of a boolean column.
    However, `patients.date_of_birth` is a date column.

    ```pycon
    --8<-- 'includes/code/tutorial/writing-a-dataset-definition/asthma_medications-pycon-success/session.txt:define_population'
    ```

    ```pycon
    --8<-- 'includes/code/tutorial/writing-a-dataset-definition/asthma_medications-pycon-success/session.txt:patients_birthdate'
    ```

    To transform a date column into a boolean column,
    use `.is_on_or_before` with a date.

    ```pycon
    --8<-- 'includes/code/tutorial/writing-a-dataset-definition/asthma_medications-pycon-success/session.txt:before_date'
    ```

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
--8<-- 'includes/code/tutorial/writing-a-dataset-definition/asthma_medications-standalone-success/analysis/dataset_definition.py:asthma_medications'
```

??? tip "Unpack the filter, the sort, and the select"
    Define a list of asthma codes.

    ```pycon
    --8<-- 'includes/code/tutorial/writing-a-dataset-definition/asthma_medications-pycon-success/session.txt:asthma_codes'
    ```

    `medications.dmd_code` is a code column.

    ```pycon
    --8<-- 'includes/code/tutorial/writing-a-dataset-definition/asthma_medications-pycon-success/session.txt:dmd_code'
    ```

    Create a filter condition in the form of a boolean column.

    ```pycon
    --8<-- 'includes/code/tutorial/writing-a-dataset-definition/asthma_medications-pycon-success/session.txt:dmd_in'
    ```

    **Filter** the `medications` table,
    so that it contains rows that match the asthma codes on the list.

    ```pycon
    --8<-- 'includes/code/tutorial/writing-a-dataset-definition/asthma_medications-pycon-success/session.txt:medications_where'
    ```

    **Sort** the resulting table by date,
    so that the most recent asthma medication is the last row for each patient.

    ```pycon
    --8<-- 'includes/code/tutorial/writing-a-dataset-definition/asthma_medications-pycon-success/session.txt:medications_sort'
    ```

    From the resulting table,
    **select** the last row for each patient.

    ```pycon
    --8<-- 'includes/code/tutorial/writing-a-dataset-definition/asthma_medications-pycon-success/session.txt:medications_last'
    ```

## Add the date column to the dataset

Select the date column and add it to the dataset.

```python
--8<-- 'includes/code/tutorial/writing-a-dataset-definition/asthma_medications-standalone-success/analysis/dataset_definition.py:medication_date'
```

## Add the code column to the dataset

Select the code column and add it to the dataset.

```python
--8<-- 'includes/code/tutorial/writing-a-dataset-definition/asthma_medications-standalone-success/analysis/dataset_definition.py:medication_code'
```

## Save the dataset definition

1. Click the menu icon towards the top left of the codespace

    ![VS Code's menu icon](menu_icon.png){ width=50 }

1. Click **File > Save**
