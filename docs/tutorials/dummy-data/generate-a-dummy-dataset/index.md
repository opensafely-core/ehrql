First, in your Codespace, modify `analysis/dataset_definition.py` to build a minimal dataset definition, as shown below.
This ehrQL code finds patients aged between 18 and 80, and adds their age, sex and date of their first
clinical event to the dataset:

:fontawesome-solid-code: `analysis/dataset_definition.py`
```py
from ehrql import create_dataset
from ehrql.tables.core import patients, clinical_events

dataset = create_dataset()

age = patients.age_on("2020-03-31")
first_event_date = clinical_events.sort_by(clinical_events.date).first_for_patient().date

dataset.define_population((age > 18) & (age < 80))
dataset.age = age
dataset.sex = patients.sex
dataset.first_event_date = first_event_date
```

:octicons-terminal-16: Try generating a dummy dataset. In the terminal, run:

```sh
opensafely exec ehrql:v1 generate-dataset analysis/dataset_definition.py
```

!!! info "`opensafely exec` vs `opensafely run`"
    We will be using `opensafely exec` for this part of the tutorial. This lets us
    run ehrQL commands as standalone actions. Refer to the documentation on
    [running ehrQL](../../../explanation/running-ehrql.md) for more information.


By default, this generates 10 patients and will print them to the terminal:

```bash
patient_id,age,sex,first_event_date
1,65,unknown,1961-07-26
2,67,intersex,1967-11-13
3,49,unknown,1974-02-08
4,74,unknown,1983-10-07
5,23,intersex,2000-02-09
6,64,male,
7,40,unknown,
8,68,male,
9,49,male,1971-05-23
10,50,intersex,1970-06-28
```

Note that all 10 patients have been generated with ages within the expected range (18-80, as defined in the dataset definition) and sex in one of the 4 possible values.

???+ example "Update the dataset definition"

    Try updating the dataset definition to filter to only female patients. Rerun the `generate-dataset` command, and confirm that the output dataset now contains 10 female patients.


:fontawesome-solid-code: If you want to produce a different number of patients, you can configure your dummy data by adding:

```py
dataset.configure_dummy_data(population_size=50)
```

???+ example "Change population size"
    Try re-running the `generate-dataset` command above, but with a different population size.

??? "Writing datasets to a file instead of the terminal"
    In this tutorial, we are letting ehrQL just print the dummy dataset it generates to the
    terminal. If you want to output the dataset as a file instead, you can pass an output argument, e.g.
    ```sh
    opensafely exec ehrql:v1 generate-dataset analysis/dataset_definition.py --output output/dataset.csv
    ```

### Characteristics of native dummy data in OpenSAFELY

In this section we have allowed ehrQL to generate dummy data using our dataset definition.

A dummy dataset produced from a dataset definition is:

- **structurally valid**
    - it will contain the correct columns, as defined in the dataset definition
    - data in each column will be of the correct type
    - where a column contains categorical data, the column values will respect the categories.  These could be categories that are built into ehrQL's definition of the underlying table (e.g. `sex` in the previous example) or they could be defined in the dataset definition using the [`case` function](../../../reference/language.md#case).

- **logically valid**
    - it will respect logic within the dataset definition itself.
    - e.g., it won't produce a clinical event date before a patient's date of birth or after their date of death.

- **consistent**
    - the generated dataset will be the same across multiple runs of the same dataset definition
    - although the data generated is random, it is "seeded", which means that the same data will be generated each time.

???+ example "Check dummy datasets are logically valid"
    :fontawesome-solid-code: try this out by adding to `analysis/dataset_definition.py`:

    ```py
    from ehrql.tables.core import patients, clinical_events
    ...
    dataset.after_dob = first_event_date > patients.date_of_birth
    dataset.before_dod = (first_event_date < patients.date_of_death) | patients.date_of_death.is_null()
    ```

    These two additional variables will return True (T) if the clinical event is within
    the patient's lifespan.

    Generate the dataset again and confirm that event dates are always after the patient's
    date of birth and before their date of death.

    :octicons-terminal-16:
    ```sh
    opensafely exec ehrql:v1 generate-dataset analysis/dataset_definition.py

    ...
    patient_id,age,sex,first_event_date,after_dob,before_dod
    1,45,unknown,2007-04-29,T,T
    2,67,intersex,1976-11-09,T,T
    3,49,male,1988-12-06,T,T
    4,74,unknown,1967-06-01,T,T
    5,23,unknown,1998-09-03,T,T
    ...
    ```

???+ example "Check dummy datasets are consistent"
    Confirm for yourself that dummy datasets are consitent running the `generate-dataset` command several times and checking the output dataset from each run.

    :octicons-terminal-16:
    ```sh
    opensafely exec ehrql:v1 generate-dataset analysis/dataset_definition.py
    ```

Next: [Generate dummy tables](../provide-dummy-tables/index.md)
