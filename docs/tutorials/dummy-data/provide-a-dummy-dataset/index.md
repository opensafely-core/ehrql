If ehrQL's native dummy data or custom dummy tables does not meet your study needs, you
have the option to you can give ehrQL a file containing a dummy dataset. Now, when you run your
dataset definition, ehrQL will just write out the provided dummy data file as the output dataset.
This output dataset can then be used as the input for your downstream analyses.

## Create a dummy dataset

Create a file at `analysis/dummy_dataset.csv`, with the following content:

```
patient_id,age,sex,first_event_date
1,29,male,2022-10-02
2,24,male,2022-07-30
3,58,male,2018-10-02
6,29,male,2007-12-12
9,61,male,1963-04-24
10,57,male,1967-12-20
11,69,male,2023-09-02
14,76,male,2007-10-16
15,23,male,1999-06-27
17,25,male,2019-08-14
```

:octicons-terminal-16: Run the first dataset definition again, with this dummy dataset.
In the terminal, run:

```sh
opensafely exec ehrql:v1 generate-dataset analysis/dataset_definition.py --dummy-data-file analysis/dummy_dataset.csv
```

You should see the exact content of `analysis/dummy_dataset.csv` printed to the terminal.


## Validation of dummy datasets

ehrQL will validate the provided dummy dataset to ensure that all the expected columns
are present, and contain data of the expected types.

We can check how this works by creating a deliberate error.
Create an error in the dummy dataset file, for example, change an age value to a non-number:

```sh hl_lines="2"
patient_id,age,sex,first_event_date
1,twenty,male,2022-10-02
2,24,male,2022-07-30
...
```

The error in the dummy dataset is identified and reported in the terminal:

```sh
[info   ] Compiling dataset definition from analysis/dataset_definition.py
[info   ] Generating dummy dataset
[info   ] Reading dummy data from analysis/dummy_dataset.csv
FileValidationError: row 1: column 'age': invalid literal for int() with base 10: 'twenty'
```

!!! warning

    Providing a dummy dataset means that your ehrQL code will not be run as part
    of the dataset generation. The command will just validate that the provided
    dummy dataset contains all the expected columns, and that those columns contain
    data of the expected types.

    If there are patients in your dummy dataset that do not meet the expected
    criteria defined in the ehrQL code, they will still be included in the output.


Let's try changing one of our dummy patients' age so that they are too young
to be selected by the ehrQL code (remember our dataset definition selects patients between the
ages of 18 and 80 only). Patient 1 does not meet the dataset criteria.

```sh hl_lines="2"
patient_id,age,sex,first_event_date
1,2,male,2022-10-02
2,24,male,2022-07-30
...
```

When we run the dataset again with this dummy dataset, there are no validation errors,
and this "invalid" patient is still included.

```
[info   ] Generating dummy dataset
[info   ] Reading dummy data from analysis/dummy_dataset.csv
patient_id,age,sex,first_event_date
1,2,male,2022-10-02
2,24,male,2022-07-30
3,58,male,2018-10-02
...
```

As the ehrQL code is not run against any data, there can also be errors in your
ehrql code that are undetected if you use a dummy dataset.

Let's introduce an error in our first dataset definition. Modify the `dataset.define_population`
line so that it is querying incorrectly; the change in the code below means that
we're extracting patients who are (impossibly) both under 18 and over 80:

:fontawesome-solid-code: `analysis/dataset_definition.py`
```py
...
dataset.define_population((age < 18) & (age > 80))
...
```

:octicons-terminal-16:
Now run this dataset definition and let ehrQL generate the output for you, using its
native dummy data:

```sh
opensafely exec ehrql:v1 generate-dataset analysis/dataset_definition.py
```

We get an error because this population definition is impossible:
```
ehrql.exceptions.CannotGenerate: Unable to find any values for date_of_birth that satisfy the population definition.
```

:octicons-terminal-16:
Now try running it again with the provided dummy dataset:

```sh
opensafely exec ehrql:v1 generate-dataset analysis/dataset_definition.py --dummy-data-file analysis/dummy_dataset.csv
```

You should again see the exact content of `analysis/dummy_dataset.csv` printed to the terminal - the error in the
ehrQL population definition is not identified.
