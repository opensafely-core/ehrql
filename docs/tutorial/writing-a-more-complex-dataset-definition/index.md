In this section, you will write the following dataset definition.

```python
---8<-- 'tutorial/example-study/dataset_definition.py'
```

## Assign the index date to a variable

We define the population,
and several demographic, exposure, and outcome variables,
relative to an index date.
Rather than repeatedly type the index date,
it's less error-prone to assign it to a variable.

```python
index_date = "2023-10-01"
```

## Create the dataset

We create the dataset with the `create_dataset` function, which we import now.

```python
from ehrql import create_dataset
```

We must assign the dataset to a variable called `dataset`.

```python
dataset = create_dataset()
```

## Define the population

To be included in the population, a patient:

* is female or male
* was an adult on the index date
* was alive on the index date
* was registered with a GP practice on the index date

!!! tip "*is* vs *was*"
    The values of some of these characteristics don't change over time;
    their values on the date the dataset is generated are the same as their values on the index date.
    We prefix such characteristics with *is*.
    However, the values of some of these characteristics might change over time;
    their values on the date the dataset is generated might be different to their values on the index date.
    We prefix such characteristics with *was*.

These characteristics come from the `patients` and the `practice_registrations` tables,
which we import now.

```python
from ehrql.tables.tpp import patients, practice_registrations
```

### Is a patient female or male?

We query the `patients.sex` column to determine whether a patient is female or male.
Rows that match the strings `"female"` or `"male"` return `True`.
Rows that don't match return `False`.
We assign the result column to the `is_female_or_male` variable.

```python
is_female_or_male = patients.sex.is_in(["female", "male"])
```

!!! tip "Strings and lists"
    We enclose characters in double quotes to create strings,
    meaning that `"female"` and `"male"` are strings.
    We use lists to group items, such as strings, together.
    We enclose items in square brackets to create lists,
    meaning that `["female", "male"]` is a list of strings.

Notice that

```python
patients.sex
```

is a column of strings but

```python
patients.sex.is_in(["female", "male"])
```

is a column of Booleans,
meaning that `is_female_or_male` is a column of Booleans.

### Was a patient an adult on the index date?

We call `patients.age_on` to determine whether a patient was an adult
— 18 or over and 110 or under —
on the index date.
We assign the result column to the `was_adult` variable.

```python
was_adult = (patients.age_on(index_date) >= 18) & (
    patients.age_on(index_date) <= 110
)
```

Notice that

```python
patients.age_on(index_date)
```

is a column of integers but

```python
patients.age_on(index_date) >= 18
```

is a column of Booleans.

Notice that we combine the two columns of Booleans with the `&` operator (AND),
meaning that `was_adult` is a column of Booleans.

!!! tip "Operator precedence"
    Normally, the `&` operator has a higher precedence than the `>=` and `<=` operators.
    However, we want the statements that include the `>=` and `<=` operators to have higher precedence,
    so we enclose them in parentheses.
    What do you think would happen if these statements didn't have higher precedence?

### Was a patient alive on the index date?

We query the `patients.date_of_death` column to determine whether a patient was alive on the index date.

* If a patient died after the index date, then the patient was alive on the index date.
* If a patient's date of death is null, then the patient was alive on the index date.

We assign the result column to the `was_alive` variable.

```python
was_alive = (
    patients.date_of_death.is_after(index_date)
    | patients.date_of_death.is_null()
)
```

Notice that rows where the date of death is after the index date return `True`;
other rows return `False`.
In other words, the result is a column of Booleans.

```python
patients.date_of_death.is_after(index_date)
```

Notice that rows where the date of death is null return `True`;
other rows return `False`.
In other words, the result is a column of Booleans.

```python
patients.date_of_death.is_null()
```

Notice that we combine the two columns of Booleans with the `|` operator (OR),
meaning that `was_alive` is a column of Booleans.

### Was a patient registered with a GP practice on the index date?

We call `practice_registrations.for_patient_on` and then query the result table
to determine whether a patient was registered with a GP practice on the index date.
We assign the result column to the `was_registered` variable.

```python
was_registered = practice_registrations.for_patient_on(
    index_date
).exists_for_patient()
```

Notice that

```python
practice_registrations
```

is a many rows per patient table, but

```python
practice_registrations.for_patient_on(index_date)
```

is a one row per patient table.

Notice that

```python
practice_registrations.for_patient_on(
    index_date
).exists_for_patient()
```

is a column of Booleans,
meaning that `was_registered` is a column of Booleans.

### Define the population

We combine the above variables with the `&` operator (AND)
and pass the result column to `dataset.define_population`.

```python
dataset.define_population(
    is_female_or_male
    & was_adult
    & was_alive
    & was_registered
)
```

Notice that because we use variables with descriptive names,
we can easily reason about the population.

## Assign variables to the dataset

We assign a variable to the dataset by adding a dot and the name of the variable to the dataset,
followed by an equals sign and the definition of the variable.
In the following example, the name of the variable is `my_variable`
and the definition of the variable is `...`.

``` { .python .no-copy }
dataset.my_variable = ...
```

### Codelists

The repository contains two codelists that we use when we assign demographic and exposure variables to the dataset.
They are stored in two CSV files.
We read each CSV file using the `codelist_from_csv` function, which we import now.

```python
from ehrql import codelist_from_csv
```

!!! tip "Codelists"
    Codelists are beyond the scope of the tutorial.
    If you would like to know more about them in general,
    then please read "[What are codelists and how are they constructed?](https://www.bennett.ox.ac.uk/blog/2023/09/what-are-codelists-and-how-are-they-constructed/)"
    on the Bennett Institute blog.
    If you would like to know more about them specifically in OpenSAFELY,
    then please read "[Introduction to codelists](https://docs.opensafely.org/codelist-intro/)".

### Demographic variables

#### Sex and age

We assign `patients.sex` to `dataset.sex`.
Remember that to be included in the population,
a patient is female or male.

```python
dataset.sex = patients.sex
```

We call `patients.age_on` to determine the age of a patient on the index date
and assign the result column to `dataset.age`.
Remember that to be included in the population,
a patient was an adult on the index date.

```python
dataset.age = patients.age_on(index_date)
```

#### Ethnicity

We use the
"[Ethnicity](https://www.opencodelists.org/codelist/opensafely/ethnicity/2020-04-27/)"
codelist to query the `clinical_events` table as well as to convert from 266 codes to six groups.

The codelist is stored in `codelists/opensafely-ethnicity.csv`.
If we open the CSV file,
then we see that the `Code` column contains the codes and that the `Grouping_6` column contains the groups.

First, we use the `codelist_from_csv` function to read the CSV file.

```python
ethnicity_codelist = codelist_from_csv(
    "codelists/opensafely-ethnicity.csv",
    column="Code",
    category_column="Grouping_6",
)
```

Notice that because we specified `column` and `category_column`,

```python
ethnicity_codelist
```

shows pairs of codes and groups.

!!! tip "Dictionaries"
    `ethnicity_codelist` is a *dictionary*, or a data structure that maps from unique keys to values.
    In this case, the keys are strings that represent codes and the values are strings that represent groups.
    We separate keys from values with colons,
    and enclose key-value pairs  in curly brackets to create dictionaries,
    meaning that `{"my_key": "my_value}` is a dictionary of one key-value pair,
    where the key and the value are strings.

Next, we import the `clinical_events` table.

```python
from ehrql.tables.tpp import clinical_events
```

Finally, we query the table
and assign the result column to `dataset.ethnicity`.

```python
dataset.ethnicity = (
    clinical_events.where(
        clinical_events.ctv3_code.is_in(ethnicity_codelist)
    )
    .sort_by(clinical_events.date)
    .last_for_patient()
    .ctv3_code.to_category(ethnicity_codelist)
)
```

Notice that we:

* Filter the table using the codelist
* Sort the result table
* Select the last row for each patient

#### Index of Multiple Deprivation

```python
from ehrql import case, when
from ehrql.tables.tpp import addresses
```

```python
imd_rounded = addresses.for_patient_on(
    index_date
).imd_rounded
max_imd = 32844
dataset.imd_quintile = case(
    when(imd_rounded < int(max_imd * 1 / 5)).then(1),
    when(imd_rounded < int(max_imd * 2 / 5)).then(2),
    when(imd_rounded < int(max_imd * 3 / 5)).then(3),
    when(imd_rounded < int(max_imd * 4 / 5)).then(4),
    when(imd_rounded <= max_imd).then(5),
)
```

### Exposure variables

#### Number of medications

We use the
[Asthma Inhaler Salbutamol Medication](https://www.opencodelists.org/codelist/opensafely/asthma-inhaler-salbutamol-medication/2020-04-15/)
codelist to query the `medications` table.

The codelist is stored in `codelists/opensafely-asthma-inhaler-salbutamol-medication.csv`.
If we open the CSV file,
then we see that the `code` column contains the codes.

First, we use the `codelist_from_csv` function to read the CSV file.

```python
asthma_inhaler_codelist = codelist_from_csv(
    "codelists/opensafely-asthma-inhaler-salbutamol-medication.csv",
    column="code",
)
```

Notice that because we specified only `column`,

```python
asthma_inhaler_codelist
```

shows only codes.

Next, we import the `medications` table.

```python
from ehrql.tables.tpp import medications
```

Finally, we query the table
and assign the result column to `dataset.num_asthma_inhaler_medications`.

```python
dataset.num_asthma_inhaler_medications = medications.where(
    medications.dmd_code.is_in(asthma_inhaler_codelist)
    & medications.date.is_on_or_between(
        index_date - days(30), index_date
    )
).count_for_patient()
```

Notice that we:

* Filter the table using the codelist and a date range
* Count the number of rows for each patient

### Outcome variables

#### Date of first admission

First, we import the `hospital_admissions` table.

```python
from ehrql.tables.tpp import hospital_admissions
```

Finally, we query the table
and assign the result column to `dataset.date_of_first_admission`.

```python
dataset.date_of_first_admission = (
    hospital_admissions.where(
        hospital_admissions.admission_date.is_after(
            index_date
        )
    )
    .sort_by(hospital_admissions.admission_date)
    .first_for_patient()
    .admission_date
)
```

Notice that we:

* Filter the table using a date range
* Sort the result table
* Select the first row for each patient

### First filter, then reduce

The ethnicity, number of medications, and date of first admission variables follow a pattern:
first filter, then reduce.
The filter steps involve filtering by a codelist,
or by a codelist and a date range.
The reduce steps involve
sorting and then selecting the first or last row,
or counting the number of rows.

By first filtering, then reducing
we transform a many rows per patient table into a one row per patient table.
